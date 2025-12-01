/* Copyright (c) 2021-25 MIT 6.102/6.031 course staff, all rights reserved.
 * Redistribution of original or derived work requires permission of course staff.
 */

import assert from 'node:assert';
import fs from 'node:fs';

/**
 * Represents a card spot on the board
 */
type Spot = {
    card: string | null;  // null means no card (removed)
    faceUp: boolean;
    controller: string | null;  // player ID or null
};

/**
 * Player state for tracking game progress
 */
type PlayerState = {
    firstCard: { row: number; column: number } | null;
    secondCard: { row: number; column: number } | null;
    matched: boolean;
    lastRevealed: Set<string>; // Track all cards revealed in current play (as "row,column" keys)
};

/**
 * Mutable game board for Memory Scramble.
 * Supports concurrent players following game rules.
 */
export class Board {

    private readonly rows: number;
    private readonly columns: number;
    private readonly grid: Array<Array<Spot>>;
    private readonly players: Map<string, PlayerState>;
    private readonly waitingForCard: Map<string, Array<() => void>>;
    private readonly watchers: Array<() => void>;
    private readonly playerLocks: Map<string, Promise<void>>; // serialize per-player flips

    // Abstraction function:
    //   Represents a Memory Scramble game board with a grid of cards.
    //   grid[row][column] represents the card at position (row, column).
    //   players maps player IDs to their current game state (cards controlled).
    //   waitingForCard maps "row,column" keys to players waiting for that card.
    //   watchers is a list of callbacks waiting for board changes.
    
    // Representation invariant:
    //   - rows > 0 and columns > 0
    //   - grid.length === rows
    //   - for all i, grid[i].length === columns
    //   - for each spot: if faceUp is true and controller is not null, that player exists in players
    //   - for each player: if firstCard/secondCard is not null, those coordinates are valid
    //   - a card can only be controlled by one player at a time
    
    // Safety from rep exposure:
    //   - All fields are private and readonly
    //   - grid, players, waitingForCard, and watchers are never returned directly
    //   - Methods return strings (board state)
    //  or primitives only

    /**
     * Create a new board with given dimensions and cards.
     * 
     * @param rows number of rows
     * @param columns number of columns
     * @param cards array of card strings in row-major order
     */
    private constructor(rows: number, columns: number, cards: string[]) {
        this.rows = rows;
        this.columns = columns;
        this.grid = [];
        this.players = new Map();
        this.waitingForCard = new Map();
        this.watchers = [];
        this.playerLocks = new Map();

        assert(cards.length === rows * columns, 'Wrong number of cards');

        for (let r = 0; r < rows; r++) {
            const row: Array<Spot> = [];
            for (let c = 0; c < columns; c++) {
                const cardIndex = r * columns + c;
                row.push({
                    card: cards[cardIndex] ?? '',
                    faceUp: false,
                    controller: null
                });
            }
            this.grid.push(row);
        }
        this.checkRep();
    }

    /**
     * Check the representation invariant.
     * Validates all RI conditions:
     * - Dimensions are positive
     * - Grid structure matches dimensions
     * - Controlled spots reference valid players
     * - Player card positions reference valid coordinates
     * - No card is controlled by multiple players
     */
    private checkRep(): void {
        // RI: rows > 0 and columns > 0
        assert(this.rows > 0, 'rows must be positive');
        assert(this.columns > 0, 'columns must be positive');
        
        // RI: grid.length === rows
        assert(this.grid.length === this.rows, 'grid length must equal rows');
        
        // RI: for all i, grid[i].length === columns
        for (const row of this.grid) {
            assert(row.length === this.columns, 'all rows must have columns length');
        }
        
        // RI: for each spot: if faceUp is true and controller is not null, that player exists in players
        for (let r = 0; r < this.rows; r++) {
            for (let c = 0; c < this.columns; c++) {
                const row = this.grid[r];
                assert(row !== undefined, 'row must exist');
                const spot = row[c];
                assert(spot !== undefined, 'spot must exist');
                
                if (spot.controller !== null) {
                    assert(this.players.has(spot.controller), 
                           `controller ${spot.controller} at (${r},${c}) must exist in players map`);
                }
            }
        }
        
        // RI: for each player: if firstCard/secondCard is not null, those coordinates are valid
        for (const [playerId, state] of this.players) {
            if (state.firstCard !== null) {
                assert(state.firstCard.row >= 0 && state.firstCard.row < this.rows,
                       `player ${playerId} firstCard row must be valid`);
                assert(state.firstCard.column >= 0 && state.firstCard.column < this.columns,
                       `player ${playerId} firstCard column must be valid`);
            }
            if (state.secondCard !== null) {
                assert(state.secondCard.row >= 0 && state.secondCard.row < this.rows,
                       `player ${playerId} secondCard row must be valid`);
                assert(state.secondCard.column >= 0 && state.secondCard.column < this.columns,
                       `player ${playerId} secondCard column must be valid`);
            }
        }
        
        // RI: a card can only be controlled by one player at a time
        const controlledPositions = new Map<string, string>();
        for (let r = 0; r < this.rows; r++) {
            for (let c = 0; c < this.columns; c++) {
                const row = this.grid[r];
                assert(row !== undefined);
                const spot = row[c];
                assert(spot !== undefined);
                
                if (spot.controller !== null) {
                    const key = `${r},${c}`;
                    assert(!controlledPositions.has(key),
                           `position (${r},${c}) controlled by multiple players`);
                    controlledPositions.set(key, spot.controller);
                }
            }
        }
    }

    /**
     * Make a new board by parsing a file.
     * 
     * PS4 instructions: the specification of this method may not be changed.
     * 
     * @param filename path to game board file
     * @returns a new board with the size and cards from the file
     * @throws Error if the file cannot be read or is not a valid game board
     * 
     * Preconditions:
     * - filename is a valid file path
     * - file format: first line "ROWSxCOLUMNS", followed by ROWS*COLUMNS card labels (one per line)
     * 
     * Postconditions:
     * - Returns a new Board with dimensions and cards as specified in file
     * - All cards are initially face-down and uncontrolled
     * - Throws Error if file is missing, unreadable, or malformed
     */
    public static async parseFromFile(filename: string): Promise<Board> {
        const content = await fs.promises.readFile(filename, 'utf-8');
        const lines = content.split(/\r?\n/);
        
        // Parse dimensions
        if (lines.length === 0) {
            throw new Error('Invalid board format: empty file');
        }
        
        const dimensions = lines[0]?.match(/^(\d+)x(\d+)$/);
        if (!dimensions || !dimensions[1] || !dimensions[2]) {
            throw new Error('Invalid board format: first line must be ROWxCOLUMN');
        }
        
        const rows = parseInt(dimensions[1]);
        const columns = parseInt(dimensions[2]);
        
        // Parse cards
        const cards: string[] = [];
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i];
            if (line !== undefined) {
                const trimmed = line.trim();
                if (trimmed.length > 0) {
                    cards.push(trimmed);
                }
            }
        }
        
        if (cards.length !== rows * columns) {
            throw new Error(`Expected ${rows * columns} cards, found ${cards.length}`);
        }
        
        return new Board(rows, columns, cards);
    }

    /**
     * Get the current board state from a player's perspective.
     * 
     * @param playerId the player viewing the board
     * @returns string representation of the board state
     * 
     * Preconditions:
     * - playerId is a non-empty string
     * 
     * Postconditions:
     * - Returns board state string in format:
     *   "ROWSxCOLUMNS\n" followed by one line per card:
     *   - "none" for removed cards
     *   - "down" for face-down cards
     *   - "my CARD" for cards controlled by playerId
     *   - "up CARD" for face-up cards controlled by others or uncontrolled
     * - Does not modify board state
     * - Ensures playerId exists in players map (creates if needed)
     */
    public async look(playerId: string): Promise<string> {
        this.ensurePlayer(playerId);
        return this.boardStateFor(playerId);
    }

    /**
     * Attempt to flip a card at the given position.
     * 
     * @param playerId the player making the flip
     * @param row the row coordinate
     * @param column the column coordinate
     * @returns the new board state from player's perspective
     * @throws Error if flip fails per game rules
     * 
     * Preconditions:
     * - playerId is a non-empty string
     * - 0 <= row < rows
     * - 0 <= column < columns
     * 
     * Postconditions:
     * - If this is player's first card:
     *   - Rule 1-A: throws Error if no card at position
     *   - Rule 1-B: flips card face-up and takes control if face-down
     *   - Rule 1-C: takes control if face-up but uncontrolled
     *   - Rule 1-D: waits if controlled by another player, then retries once
     * - If this is player's second card:
     *   - Rule 2-A: throws Error if no card at position, relinquishes first card
     *   - Rule 2-B: throws Error if card is controlled, relinquishes first card
     *   - Rule 2-C: flips card face-up if needed
     *   - Rule 2-D: if cards match, keeps control of both
     *   - Rule 2-E: if cards don't match, relinquishes control of first card
     * - Rule 3: if player has completed previous play, cleans it up first:
     *   - Rule 3-A: removes matched cards
     *   - Rule 3-B: turns non-matched cards face-down
     * - Serializes flip operations per player (no interleaving for same player)
     * - Returns updated board state string
     */
    public async flip(playerId: string, row: number, column: number): Promise<string> {
        // Serialize flips per player to avoid race conditions from rapid clicks or network interleaving
        return await this.runExclusive(playerId, async () => {
            this.ensurePlayer(playerId);
            const playerState = this.players.get(playerId);
            assert(playerState !== undefined);

            // Rule 3: Finish previous play if starting a new one
            // Check if player already has a first card
            if (playerState.firstCard !== null) {
                const firstRow = this.grid[playerState.firstCard.row];
                const firstSpot = firstRow?.[playerState.firstCard.column];
                
                // If the first card exists and is uncontrolled (player clicked same card twice),
                // or if we have a completed play (both cards set or matched), clean it up
                const isUncontrolled = firstSpot && firstSpot.controller === null;
                const hasCompletedPlay = playerState.matched || playerState.secondCard !== null;
                
                if (isUncontrolled || hasCompletedPlay) {
                    await this.finishPreviousPlay(playerId);
                }
            }

            if (playerState.firstCard === null) {
                // Flipping first card
                return await this.flipFirstCard(playerId, row, column);
            } else {
                // Flipping second card
                return await this.flipSecondCard(playerId, row, column);
            }
        });
    }

    /**
     * Apply a transformation function to all cards on the board.
     * 
     * @param playerId the player applying the map
     * @param f transformation function
     * @returns the new board state
     * 
     * Preconditions:
     * - playerId is a non-empty string
     * - f is a mathematical function: f(c) returns same result for same input c
     * - f(c) returns a valid card label
     * 
     * Postconditions:
     * - Replaces every card label c on board with f(c)
     * - Maintains pairwise consistency: all instances of same card transform identically
     * - Does not affect card face-up/down state or controller
     * - Notifies watchers if any cards changed
     * - Can interleave with other operations without blocking
     * - Returns updated board state string
     */
    public async map(playerId: string, f: (card: string) => Promise<string>): Promise<string> {
        this.ensurePlayer(playerId);
        
        // Build a map of unique cards to their replacements
        const uniqueCards = new Set<string>();
        for (const row of this.grid) {
            for (const spot of row) {
                if (spot.card !== null && spot.card.length > 0) {
                    uniqueCards.add(spot.card);
                }
            }
        }
        
        const replacements = new Map<string, string>();
        for (const card of uniqueCards) {
            const newCard = await f(card);
            replacements.set(card, newCard);
        }
        
        // Apply replacements atomically to maintain pairwise consistency
        let changed = false;
        for (const row of this.grid) {
            for (const spot of row) {
                if (spot.card !== null && spot.card.length > 0) {
                    const newCard = replacements.get(spot.card);
                    if (newCard !== undefined && newCard !== spot.card) {
                        spot.card = newCard;
                        changed = true;
                    }
                }
            }
        }
        
        if (changed) {
            this.notifyWatchers();
        }
        
        return this.boardStateFor(playerId);
    }

    /**
     * Wait for the next board change.
     * 
     * @param playerId the player watching
     * @returns the new board state after a change
     * 
     * Preconditions:
     * - playerId is a non-empty string
     * 
     * Postconditions:
     * - Blocks until board changes (cards flip up/down, removed, or labels change)
     * - Returns updated board state string after change occurs
     * - Multiple watchers are all notified of same change
     * - Does not modify board state
     */
    public async watch(playerId: string): Promise<string> {
        this.ensurePlayer(playerId);
        
        const { promise, resolve } = Promise.withResolvers<void>();
        this.watchers.push(resolve);
        
        await promise;
        
        return this.boardStateFor(playerId);
    }

    /**
     * Ensure player exists in players map.
     */
    private ensurePlayer(playerId: string): void {
        if (!this.players.has(playerId)) {
            this.players.set(playerId, {
                firstCard: null,
                secondCard: null,
                matched: false,
                lastRevealed: new Set<string>()
            });
        }
    }

    /**
     * Flip the first card for a player.
     */
    private async flipFirstCard(playerId: string, row: number, column: number): Promise<string> {
        const rowData = this.grid[row];
        assert(rowData !== undefined, `Invalid row: ${row}`);
        const spot = rowData[column];
        assert(spot !== undefined, `Invalid column: ${column}`);
        
        const playerState = this.players.get(playerId);
        assert(playerState !== undefined);
        
        // Rule 1-A: no card there
        if (spot.card === null || spot.card.length === 0) {
            throw new Error('no card at this position');
        }
        
        // Rule 1-D: wait if controlled by another player (wait only ONCE)
        if (spot.controller !== null && spot.controller !== playerId) {
            await this.waitForCard(row, column);
            
            // After waiting, re-check conditions
            // Rule 1-A: card might have been removed while waiting
            if (spot.card === null || spot.card.length === 0) {
                throw new Error('no card at this position');
            }
            
            // If still controlled after our turn in queue, fail
            // (another player in the queue got it first, or controller didn't relinquish)
            if (spot.controller !== null && spot.controller !== playerId) {
                throw new Error('card is still controlled after waiting');
            }
        }
        
        // Rule 1-B or 1-C: take control
        if (!spot.faceUp) {
            spot.faceUp = true;
            this.notifyWatchers();
        }
        spot.controller = playerId;
        playerState.firstCard = { row, column };
        
        // Track this revealed card
        playerState.lastRevealed.add(`${row},${column}`);
        
        // After taking control, notify next waiter (if any) so they can check if they lost
        this.notifyCardAvailable(row, column);
        
        return this.boardStateFor(playerId);
    }

    /**
     * Flip the second card for a player.
     */
    private async flipSecondCard(playerId: string, row: number, column: number): Promise<string> {
        const rowData = this.grid[row];
        assert(rowData !== undefined, `Invalid row: ${row}`);
        const spot = rowData[column];
        assert(spot !== undefined, `Invalid column: ${column}`);
        
        const playerState = this.players.get(playerId);
        assert(playerState !== undefined);
        assert(playerState.firstCard !== null);
        
        const firstRow = this.grid[playerState.firstCard.row];
        assert(firstRow !== undefined);
        const firstSpot = firstRow[playerState.firstCard.column];
        assert(firstSpot !== undefined);
        
        // Rule 2-A: no card there
        if (spot.card === null || spot.card.length === 0) {
            const firstCardPos = playerState.firstCard;
            playerState.firstCard = null;
            firstSpot.controller = null;
            this.notifyCardAvailable(firstCardPos.row, firstCardPos.column);
            throw new Error('no card at this position');
        }
        
        // Rule 2-B: controlled by a player (including self)
        if (spot.controller !== null) {
            // Relinquish control but keep track of the card in player state
            // so finishPreviousPlay will flip it down on next play
            firstSpot.controller = null;
            this.notifyCardAvailable(playerState.firstCard.row, playerState.firstCard.column);
            throw new Error('card is controlled');
        }
        
        // Flip face up if needed (Rule 2-C)
        if (!spot.faceUp) {
            spot.faceUp = true;
            this.notifyWatchers();
        }
        
        playerState.secondCard = { row, column };
        
        // Track this revealed card
        playerState.lastRevealed.add(`${row},${column}`);
        
        // Check for match (Rule 2-D or 2-E)
        if (firstSpot.card === spot.card) {
            // Match!
            spot.controller = playerId;
            playerState.matched = true;
        } else {
            // No match
            playerState.matched = false;
            const firstCardPos = playerState.firstCard;
            firstSpot.controller = null;
            this.notifyCardAvailable(firstCardPos.row, firstCardPos.column);
        }
        
        return this.boardStateFor(playerId);
    }

    /**
     * Finish previous play before starting new first card (Rule 3).
     */
    private async finishPreviousPlay(playerId: string): Promise<void> {
        const playerState = this.players.get(playerId);
        assert(playerState !== undefined);
        
        if (playerState.firstCard === null) {
            return; // No previous play
        }
        
        const firstRow = this.grid[playerState.firstCard.row];
        assert(firstRow !== undefined);
        const firstSpot = firstRow[playerState.firstCard.column];
        assert(firstSpot !== undefined);
        
        if (playerState.matched && playerState.secondCard !== null) {
            // Rule 3-A: Remove matched cards
            const secondRow = this.grid[playerState.secondCard.row];
            assert(secondRow !== undefined);
            const secondSpot = secondRow[playerState.secondCard.column];
            assert(secondSpot !== undefined);
            
            firstSpot.card = null;
            firstSpot.faceUp = false;
            firstSpot.controller = null;
            secondSpot.card = null;
            secondSpot.faceUp = false;
            secondSpot.controller = null;
            this.notifyWatchers();
            this.notifyCardAvailable(playerState.firstCard.row, playerState.firstCard.column);
            this.notifyCardAvailable(playerState.secondCard.row, playerState.secondCard.column);
        } else {
            // Rule 3-B: Turn all previously revealed cards face down if still up and uncontrolled
            let changed = false;
            
            // Flip down the first card if it's uncontrolled
            if (firstSpot.card !== null && firstSpot.faceUp && firstSpot.controller === null) {
                firstSpot.faceUp = false;
                changed = true;
            }
            
            // Flip down any other revealed cards
            for (const key of playerState.lastRevealed) {
                const [rowStr, colStr] = key.split(',');
                const r = parseInt(rowStr ?? '0');
                const c = parseInt(colStr ?? '0');
                const rowData = this.grid[r];
                if (rowData !== undefined) {
                    const spot = rowData[c];
                    if (spot !== undefined && spot.card !== null && spot.faceUp && spot.controller === null) {
                        spot.faceUp = false;
                        changed = true;
                    }
                }
            }
            
            if (changed) {
                this.notifyWatchers();
            }
        }
        
        // Clear the state for next play
        playerState.lastRevealed.clear();
        playerState.firstCard = null;
        playerState.secondCard = null;
        playerState.matched = false;
    }

    /**
     * Wait for a card to become available (Rule 1-D).
     * 
     * Implements fair queuing: players are added to a FIFO queue for each card position.
     * When the card becomes available (controller relinquishes it), the FIRST player
     * in the queue is notified and gets ONE chance to take control.
     * 
     * This prevents a player from "spamming" clicks to eventually capture a card -
     * they must wait their turn in the queue.
     * 
     * @param row the row of the card to wait for
     * @param column the column of the card to wait for
     */
    private async waitForCard(row: number, column: number): Promise<void> {
        const key = `${row},${column}`;
        const { promise, resolve } = Promise.withResolvers<void>();
        
        if (!this.waitingForCard.has(key)) {
            this.waitingForCard.set(key, []);
        }
        const waiting = this.waitingForCard.get(key);
        assert(waiting !== undefined);
        
        // Add to end of queue (FIFO)
        waiting.push(resolve);
        
        // Wait until we're notified (when we reach front of queue)
        await promise;
    }

    /**
     * Notify waiting players that a card is available.
     * Only the FIRST player in the queue gets notified (FIFO queue for fairness).
     */
    private notifyCardAvailable(row: number, column: number): void {
        const key = `${row},${column}`;
        const waiting = this.waitingForCard.get(key);
        if (waiting && waiting.length > 0) {
            // Notify only the FIRST waiter (FIFO - fair queuing)
            const waiter = waiting.shift();
            if (waiter) {
                waiter();
            }
        }
    }

    /**
     * Notify all watchers of a board change.
     */
    private notifyWatchers(): void {
        const watchers = [...this.watchers];
        this.watchers.length = 0;
        for (const watcher of watchers) {
            watcher();
        }
    }

    /**
     * Run a task with a per-player mutex to ensure sequential flip operations for the same player.
     * Different players can still operate concurrently.
     */
    private async runExclusive<T>(playerId: string, task: () => Promise<T>): Promise<T> {
        const prev = this.playerLocks.get(playerId) ?? Promise.resolve();
        let release: (() => void) | undefined;
        const gate = new Promise<void>(resolve => { release = resolve; });
        // Chain our gate after the previous promise
        this.playerLocks.set(playerId, prev.then(() => gate));

        // Wait for previous operations to finish
        await prev;
        try {
            return await task();
        } finally {
            // Release our gate to allow the next queued operation (if any)
            release?.();
            // If nothing else is queued, cleanup the lock map entry eventually
            // (safe to delete; future operations will recreate the chain)
            // Note: we don't wait for gate to resolve here to avoid deadlocks
            // under unexpected exceptions.
            // Best-effort cleanup:
            if (this.playerLocks.get(playerId) === gate) {
                this.playerLocks.delete(playerId);
            }
        }
    }

    /**
     * Generate board state string for a player.
     */
    private boardStateFor(playerId: string): string {
        let result = `${this.rows}x${this.columns}\n`;
        
        for (let r = 0; r < this.rows; r++) {
            for (let c = 0; c < this.columns; c++) {
                const rowData = this.grid[r];
                assert(rowData !== undefined);
                const spot = rowData[c];
                assert(spot !== undefined);
                
                if (spot.card === null || spot.card.length === 0) {
                    result += 'none\n';
                } else if (!spot.faceUp) {
                    result += 'down\n';
                } else if (spot.controller === playerId) {
                    result += `my ${spot.card}\n`;
                } else {
                    result += `up ${spot.card}\n`;
                }
            }
        }
        
        return result;
    }

    /**
     * String representation of the board (for debugging).
     */
    public toString(): string {
        return `Board(${this.rows}x${this.columns})`;
    }
}
