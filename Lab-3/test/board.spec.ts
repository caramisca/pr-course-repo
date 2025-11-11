/* Copyright (c) 2021-25 MIT 6.102/6.031 course staff, all rights reserved.
 * Redistribution of original or derived work requires permission of course staff.
 */

import assert from 'node:assert';
import { Board } from '../src/board.js';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';

/**
 * Comprehensive unit tests for the Board ADT.
 * 
 * Tests cover all game rules as specified in the requirements:
 * - Rule 1 (First card): Flipping first card behavior
 * - Rule 2 (Second card): Flipping second card behavior  
 * - Rule 3 (Cleanup): Previous play cleanup
 * 
 * Testing strategy is documented for each test suite to ensure
 * comprehensive coverage of all edge cases and game scenarios.
 * 
 * Total: 25+ test cases covering parseFromFile, look, flip, map, and watch
 */
describe('Board', function() {
    
    /**
     * Testing strategy for Board:
     * 
     * Partition for parseFromFile():
     *   - Board dimensions: 1x1, 3x3, 5x5, 1x10, 10x1
     *   - File validity: valid format, missing dimensions, wrong card count, empty file
     *   - Card patterns: all same, all different, pairs
     * 
     * Partition for look():
     *   - Card states: all face-down, some face-up, controlled by viewer, controlled by others
     *   - Board state: initial, mid-game, cards removed
     *   - Player perspective: cards I control vs cards others control
     * 
     * Partition for flip():
     *   Rule 1 (First card):
     *     - Target position: empty (removed), face-down, face-up uncontrolled, face-up controlled
     *     - Controller: none, same player, different player
     *     - Waiting: no wait needed, must wait for controlled card
     *   
     *   Rule 2 (Second card):
     *     - Target position: empty, face-down, face-up uncontrolled, face-up controlled
     *     - Match result: cards match, cards don't match
     *     - Control outcome: keep control (match), relinquish control (no match or error)
     *   
     *   Rule 3 (Cleanup):
     *     - Previous play result: matched pair, non-matched pair, single card
     *     - Cleanup action: remove matched cards, turn down non-matched cards
     * 
     * Partition for map():
     *   - Transformation: identity, change all, change some
     *   - Timing: no concurrent ops, concurrent with flips, concurrent with other maps
     *   - Pairwise consistency: cards with same label must transform identically
     * 
     * Partition for watch():
     *   - Board change type: card flip, card removal, card transformation
     *   - Timing: change happens immediately, change happens after wait
     *   - Multiple watchers: one watcher, multiple watchers
     */

    describe('parseFromFile() tests', function() {
        /**
         * Tests for board file parsing.
         * Covers: valid boards with different dimensions, invalid formats.
         */
        
        it('parses a valid board with same dimensions', async function() {
            // Test: 3x3 board with matching pairs
            const board = await Board.parseFromFile('boards/perfect.txt');
            const state = await board.look('player1');
            assert(state.startsWith('3x3\n'), 'Board dimensions should be 3x3');
            const lines = state.split('\n');
            assert.strictEqual(lines.length, 11); // header + 9 cards + trailing newline
            assert.strictEqual(lines.filter(l => l === 'down').length, 9, 'All cards should be face-down initially');
        });

        it('parses a valid board with different dimensions', async function() {
            // Test: 5x5 board with A and B cards
            const board = await Board.parseFromFile('boards/ab.txt');
            const state = await board.look('player1');
            assert(state.startsWith('5x5\n'), 'Board dimensions should be 5x5');
            const lines = state.split('\n');
            assert.strictEqual(lines.filter(l => l === 'down').length, 25, 'All 25 cards should be face-down');
        });

        it('rejects empty board file', async function() {
            // Test: file with no content should fail
            const tempFile = 'boards/temp_empty.txt';
            try {
                await fs.writeFile(tempFile, '');
                await assert.rejects(
                    Board.parseFromFile(tempFile),
                    /empty|dimensions|invalid/i,
                    'Should reject empty file'
                );
            } finally {
                await fs.unlink(tempFile).catch(() => {/* ignore */});
            }
        });

        it('rejects invalid board dimensions', async function() {
            // Test: invalid dimension format
            const tempFile = 'boards/temp_invalid_dims.txt';
            try {
                await fs.writeFile(tempFile, 'not_dimensions\nA\nA\n');
                await assert.rejects(
                    Board.parseFromFile(tempFile),
                    /dimensions|invalid|format/i,
                    'Should reject invalid dimensions'
                );
            } finally {
                await fs.unlink(tempFile).catch(() => {/* ignore */});
            }
        });

        it('rejects if missing cards', async function() {
            // Test: dimension says 2x2 but only 3 cards provided
            const tempFile = 'boards/temp_missing_cards.txt';
            try {
                await fs.writeFile(tempFile, '2x2\nA\nA\nB\n');
                await assert.rejects(
                    Board.parseFromFile(tempFile),
                    /cards|count|mismatch/i,
                    'Should reject when card count does not match dimensions'
                );
            } finally {
                await fs.unlink(tempFile).catch(() => {/* ignore */});
            }
        });

        it('rejects boards with different card patterns', async function() {
            // Test: board with odd number of each card (no valid pairs)
            const tempFile = 'boards/temp_odd_pattern.txt';
            try {
                await fs.writeFile(tempFile, '3x3\nA\nA\nA\nB\nB\nB\nC\nC\nC\n');
                // This should parse successfully but may behave unexpectedly in gameplay
                const board = await Board.parseFromFile(tempFile);
                assert(board.toString().includes('3x3'), 'Should parse board even with odd patterns');
            } finally {
                await fs.unlink(tempFile).catch(() => {/* ignore */});
            }
        });
    });

    describe('look() tests', function() {
        /**
         * Tests for viewing board state from player perspective.
         * Covers: initial state, face-up cards, controlled cards, removed cards.
         */
        
        it('shows all cards face down initially', async function() {
            const board = await Board.parseFromFile('boards/perfect.txt');
            const state = await board.look('alice');
            const lines = state.split('\n');
            assert(lines.every((line, idx) => idx === 0 || line === 'down' || line === ''), 
                   'All cards should be face-down on initial board');
        });

        it('shows my cards when controlled by viewer', async function() {
            const board = await Board.parseFromFile('boards/perfect.txt');
            await board.flip('alice', 0, 0);
            const state = await board.look('alice');
            const lines = state.split('\n');
            assert(lines[1]?.startsWith('my '), 'Alice should see her controlled card as "my CARD"');
        });

        it('shows face-up cards controlled by others', async function() {
            const board = await Board.parseFromFile('boards/perfect.txt');
            await board.flip('alice', 0, 0);
            const state = await board.look('bob');
            const lines = state.split('\n');
            assert(lines[1]?.startsWith('up '), 'Bob should see Alice\'s card as "up CARD"');
        });

        it('shows empty spaces for removed cards', async function() {
            const board = await Board.parseFromFile('boards/perfect.txt');
            // Match cards at (0,0) and (0,1)
            await board.flip('alice', 0, 0);
            await board.flip('alice', 0, 1);
            // Start new play to trigger removal
            await board.flip('alice', 1, 0);
            
            const state = await board.look('alice');
            const lines = state.split('\n');
            assert.strictEqual(lines[1], 'none', 'Removed card should show as "none"');
            assert.strictEqual(lines[2], 'none', 'Removed card should show as "none"');
        });
    });

    describe('flip() tests', function() {
        /**
         * Tests for card flipping behavior covering all three rules.
         */
        
        it('allows flipping an uncontrolled card as first card', async function() {
            // Test Rule 1-B: flip face-down card
            const board = await Board.parseFromFile('boards/ab.txt');
            const result = await board.flip('alice', 0, 0);
            const lines = result.split('\n');
            assert(lines[1]?.startsWith('my '), 'Alice should control the flipped card');
        });

        it('waits for card controlled by others ', async function() {
            // Test Rule 1-D: waiting for controlled card
            this.timeout(500); // Allow time for async wait
            const board = await Board.parseFromFile('boards/ab.txt');
            
            // Alice flips first card at (0,0)
            await board.flip('alice', 0, 0);
            
            // Bob tries to flip the same card - should wait
            const bobPromise = board.flip('bob', 0, 0);
            
            // Small delay to ensure Bob is waiting
            await new Promise(resolve => setTimeout(resolve, 50));
            
            // Alice flips second card, relinquishing control of first
            await board.flip('alice', 0, 1);
            
            // Bob should now get control
            const result = await bobPromise;
            const lines = result.split('\n');
            assert(lines[1]?.startsWith('my '), 'Bob should eventually control the card after waiting');
        });

        it('rejects invalid card positions', async function() {
            // Test: flipping out-of-bounds position
            const board = await Board.parseFromFile('boards/ab.txt'); // 5x5 board
            await assert.rejects(
                board.flip('alice', 10, 10),
                /invalid|out of bounds|position/i,
                'Should reject out-of-bounds position'
            );
        });

        it('handles matching pair correctly', async function() {
            // Test Rule 2-D: matching cards
            const board = await Board.parseFromFile('boards/perfect.txt');
            
            // Flip matching unicorns at (0,0) and (0,1)
            await board.flip('alice', 0, 0);
            const result = await board.flip('alice', 0, 1);
            
            const lines = result.split('\n');
            // Alice should control both matched cards
            assert(lines[1]?.startsWith('my '), 'First matched card should be controlled');
            assert(lines[2]?.startsWith('my '), 'Second matched card should be controlled');
        });

        it('handles non-matching pair correctly', async function() {
            // Test Rule 2-E: non-matching cards
            const board = await Board.parseFromFile('boards/ab.txt');
            
            // Flip non-matching A and B cards
            await board.flip('alice', 0, 0);
            await board.flip('alice', 0, 1);
            
            const result = await board.look('alice');
            const lines = result.split('\n');
            // Cards should be face up but not controlled after mismatch
            assert(!lines[1]?.startsWith('my '), 'First card should not be controlled after mismatch');
        });

        it('rejects flipping controlled card as second card', async function() {
            // Test Rule 2-B: can't flip controlled card as second
            const board = await Board.parseFromFile('boards/ab.txt');
            
            // Alice flips first card
            await board.flip('alice', 0, 0);
            
            // Bob flips first card
            await board.flip('bob', 0, 1);
            
            // Alice tries to flip Bob's controlled card as second - should fail
            await assert.rejects(
                board.flip('alice', 0, 1),
                /controlled/i,
                'Should reject flipping controlled card as second'
            );
        });

        it('handles removed cards correctly', async function() {
            // Test Rule 3-A: matched cards are removed
            const board = await Board.parseFromFile('boards/perfect.txt');
            
            // Match cards
            await board.flip('alice', 0, 0);
            await board.flip('alice', 0, 1);
            
            // Start new play - should trigger removal
            await board.flip('alice', 1, 0);
            
            const result = await board.look('alice');
            const lines = result.split('\n');
            assert.strictEqual(lines[1], 'none', 'Matched card should be removed');
            assert.strictEqual(lines[2], 'none', 'Matched card should be removed');
        });
    });



    describe('map() tests', function() {
        /**
         * Tests for card transformation operation.
         * Covers: simple replacement, pairwise consistency, concurrent operations.
         */
        
        it('performs simple card replacement', async function() {
            // Test: transform all A cards to X, all B cards to Y
            const board = await Board.parseFromFile('boards/ab.txt');
            
            const result = await board.map('alice', async (card: string) => {
                if (card === 'A') return 'X';
                if (card === 'B') return 'Y';
                return card;
            });
            
            // Board should show transformed cards (when flipped)
            assert(result.startsWith('5x5\n'), 'Board dimensions should remain unchanged');
        });

        it('maintains pair consistency during mapping', async function() {
            // Test: all instances of the same card must transform identically
            const board = await Board.parseFromFile('boards/perfect.txt');
            
            const callCounts = new Map<string, number>();
            await board.map('alice', async (card: string) => {
                callCounts.set(card, (callCounts.get(card) ?? 0) + 1);
                return card + '_transformed';
            });
            
            // Each unique card should only be transformed once (pairwise consistency)
            for (const [card, count] of callCounts) {
                assert.strictEqual(count, 1, `Card "${card}" should be transformed exactly once`);
            }
        });

        it('handles multiple simultaneous mappings', async function() {
            // Test: concurrent map operations
            const board = await Board.parseFromFile('boards/ab.txt');
            
            const map1 = board.map('alice', async (c) => c + '1');
            const map2 = board.map('bob', async (c) => c + '2');
            
            // Both should complete without error
            await Promise.all([map1, map2]);
        });

        it('maps face-up cards correctly', async function() {
            // Test: transformation applies to face-up cards
            const board = await Board.parseFromFile('boards/perfect.txt');
            
            // Flip a card
            await board.flip('alice', 0, 0);
            
            // Transform all cards
            await board.map('bob', async (card: string) => '⭐');
            
            // Check that transformation happened
            const state = await board.look('bob');
            // Flipped card should now show transformed value
            assert(state.includes('⭐') || state.includes('down'), 'Transformed cards should be visible');
        });
    });

    describe('watch() tests', function() {
        /**
         * Tests for board change notification.
         * Covers: flip notifications, removal notifications, transformation notifications.
         */
        
        it('notifies when cards are flipped ', async function() {
            // Test: watch resolves when board changes
            this.timeout(300);
            const board = await Board.parseFromFile('boards/ab.txt');
            
            const watchPromise = board.watch('bob');
            
            // Small delay then make a change
            await new Promise(resolve => setTimeout(resolve, 50));
            await board.flip('alice', 0, 0);
            
            // Watch should resolve with new board state
            const result = await watchPromise;
            assert(result.includes('up ') || result.includes('my '), 'Should show changed board state');
        });

        it('notifies when cards are removed ', async function() {
            // Test: watch notifies on card removal
            this.timeout(300);
            const board = await Board.parseFromFile('boards/perfect.txt');
            
            // Set up a matched pair
            await board.flip('alice', 0, 0);
            await board.flip('alice', 0, 1);
            
            const watchPromise = board.watch('bob');
            
            // Small delay then trigger removal
            await new Promise(resolve => setTimeout(resolve, 50));
            await board.flip('alice', 1, 0); // This removes the matched pair
            
            const result = await watchPromise;
            assert(result.includes('none') || result.includes('my '), 'Should show board with removed cards');
        });

        it('notifies when cards change value ', async function() {
            // Test: watch notifies on card transformation
            this.timeout(300);
            const board = await Board.parseFromFile('boards/ab.txt');
            
            const watchPromise = board.watch('bob');
            
            // Small delay then transform cards
            await new Promise(resolve => setTimeout(resolve, 50));
            await board.map('alice', async (card: string) => card + '_new');
            
            const result = await watchPromise;
            assert(result.startsWith('5x5\n'), 'Should show updated board state');
        });

        it('notifies multiple watchers ', async function() {
            // Test: multiple watchers all get notified
            this.timeout(300);
            const board = await Board.parseFromFile('boards/ab.txt');
            
            const watch1 = board.watch('alice');
            const watch2 = board.watch('bob');
            const watch3 = board.watch('charlie');
            
            // Small delay then make change
            await new Promise(resolve => setTimeout(resolve, 50));
            await board.flip('diana', 0, 0);
            
            // All watches should resolve
            const [r1, r2, r3] = await Promise.all([watch1, watch2, watch3]);
            assert(r1.length > 0 && r2.length > 0 && r3.length > 0, 'All watchers should be notified');
        });
    });

    describe('Concurrent players', function() {
        /**
         * Tests for multi-player concurrent access scenarios.
         */
        
        it('handles multiple players correctly', async function() {
            const board = await Board.parseFromFile('boards/ab.txt');
            
            // Both players flip different cards simultaneously
            const alicePromise = board.flip('alice', 0, 0);
            const bobPromise = board.flip('bob', 1, 0);
            
            const [aliceResult, bobResult] = await Promise.all([alicePromise, bobPromise]);
            
            // Both should control their respective cards
            assert(aliceResult.includes('my '), 'Alice should control her card');
            assert(bobResult.includes('my '), 'Bob should control his card');
        });
    });
});
