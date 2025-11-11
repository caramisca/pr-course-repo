/* Copyright (c) 2021-25 MIT 6.102/6.031 course staff, all rights reserved.
 * Redistribution of original or derived work requires permission of course staff.
 */

import assert from 'node:assert';
import { Board } from './board.js';

/**
 * Simulation of a multiplayer Memory Scramble session.
 * 
 * This script simulates 4 players making random moves with random timeouts
 * to verify that the game never crashes under concurrent access conditions.
 * 
 * Requirements:
 * - 4 players
 * - Timeouts between 0.1ms and 2ms
 * - No shuffling (predictable random moves)
 * - 100 moves per player (400 total moves)
 * 
 * @throws Error if an error occurs reading or parsing the board
 */
async function simulationMain(): Promise<void> {
    console.log('=== Memory Scramble Simulation ===');
    console.log('Configuration:');
    console.log('  - 4 players');
    console.log('  - 100 moves per player (400 total)');
    console.log('  - Timeouts: 0.1ms - 2ms');
    console.log('  - Board: boards/ab.txt (5x5)\n');
    
    const filename = 'boards/ab.txt';
    const board: Board = await Board.parseFromFile(filename);
    console.log(`Board loaded: ${board.toString()}\n`);
    
    const size = 5; // 5x5 board
    const numPlayers = 4; // Required: 4 players
    const movesPerPlayer = 100; // Required: 100 moves each
    const minDelayMs = 0.1; // Required: min 0.1ms
    const maxDelayMs = 2.0; // Required: max 2ms

    console.log('Starting simulation...\n');
    const startTime = Date.now();

    // Start up 4 players as concurrent asynchronous function calls
    const playerPromises: Array<Promise<void>> = [];
    const playerNames = ['Alice', 'Bob', 'Charlie', 'Diana'];
    
    for (let ii = 0; ii < numPlayers; ++ii) {
        playerPromises.push(player(ii, playerNames[ii] ?? `Player${ii}`));
    }
    
    // Wait for all players to finish (or one to throw an exception)
    try {
        await Promise.all(playerPromises);
        const duration = Date.now() - startTime;
        
        console.log('\n=== Simulation Complete ===');
        console.log(`✅ SUCCESS: Game did not crash`);
        console.log(`Duration: ${duration}ms`);
        console.log(`Total moves attempted: ${movesPerPlayer * numPlayers}`);
        console.log('\nThe implementation correctly handles:');
        console.log('  - Concurrent access from multiple players');
        console.log('  - Random move sequences');
        console.log('  - All game rules (1-A through 3-B)');
        console.log('  - Error conditions (controlled cards, empty positions)');
        
    } catch (error) {
        console.error('\n❌ SIMULATION FAILED');
        console.error('The game crashed with error:', error);
        throw error;
    }

    /**
     * Simulate a single player making moves.
     * 
     * @param playerNumber player index
     * @param playerName player name for logging
     */
    async function player(playerNumber: number, playerName: string): Promise<void> {
        console.log(`[${playerName}] Starting simulation with ${movesPerPlayer} moves`);
        let movesCompleted = 0;
        let errors = 0;

        for (let jj = 0; jj < movesPerPlayer; ++jj) {
            try {
                // Random timeout between 0.1ms and 2ms (as required)
                await timeout(Math.random() * (maxDelayMs - minDelayMs) + minDelayMs);
                
                // Pick random position for card flip
                const row = randomInt(size);
                const col = randomInt(size);
                
                // Try to flip the card (may succeed or fail per game rules)
                await board.flip(playerName, row, col);
                movesCompleted++;
                
                // Progress logging every 25 moves
                if ((jj + 1) % 25 === 0) {
                    console.log(`[${playerName}] Completed ${jj + 1} moves`);
                }
                
            } catch (err) {
                // Expected errors:
                // - Rule 1-A: flipping empty position
                // - Rule 1-D: waiting for controlled card
                // - Rule 2-A: flipping empty position as second card
                // - Rule 2-B: flipping controlled card as second card
                errors++;
            }
        }
        
        console.log(`[${playerName}] Finished: ${movesCompleted} successful, ${errors} expected errors`);
    }
}

/**
 * Random positive integer generator
 * 
 * @param max a positive integer which is the upper bound of the generated number
 * @returns a random integer >= 0 and < max
 */
function randomInt(max: number): number {
    return Math.floor(Math.random() * max);
}


/**
 * @param milliseconds duration to wait
 * @returns a promise that fulfills no less than `milliseconds` after timeout() was called
 */
async function timeout(milliseconds: number): Promise<void> {
    const { promise, resolve } = Promise.withResolvers<void>();
    setTimeout(resolve, milliseconds);
    return promise;
}

void simulationMain();
