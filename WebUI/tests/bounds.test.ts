import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { claimBounds, initialMapBounds } from '../src/engine.ts';

const europe = { longitude: 0.1, latitude: 49.05, theater: 'western_europe' };
const norma = { longitude: -0.3, latitude: 49.3, theater: 'western_europe' };
const lunga = { longitude: 160.05, latitude: -9.43, theater: 'pacific' };
const tulagi = { longitude: 160.2, latitude: -9.1, theater: 'pacific' };

describe('claimBounds', () => {
  it('returns null when there are no coordinates', () => {
    assert.equal(claimBounds([]), null);
    assert.equal(claimBounds([{ longitude: Number.NaN, latitude: 0 }]), null);
  });
  it('covers every point', () => {
    assert.deepEqual(claimBounds([europe, norma]), [-0.3, 49.05, 0.1, 49.3]);
  });
});

describe('initialMapBounds', () => {
  const mixed = [europe, norma, lunga, tulagi];

  it('opens on western_europe when the filter is All theaters', () => {
    assert.deepEqual(initialMapBounds(mixed, ''), claimBounds([europe, norma]));
  });

  it('opens on the selected theater', () => {
    assert.deepEqual(initialMapBounds(mixed, 'pacific'), claimBounds([lunga, tulagi]));
  });

  it('does not use the global Europe-to-Pacific box', () => {
    const opening = initialMapBounds(mixed, '');
    const world = claimBounds(mixed);
    assert.ok(opening);
    assert.ok(world);
    assert.ok(opening[2] - opening[0] < 20, 'opening width should stay a campaign area');
    assert.ok(world[2] - world[0] > 100, 'the unfiltered box spans oceans');
  });

  it('falls back to the busiest theater when western_europe is absent', () => {
    const africa = [
      { longitude: 10, latitude: 36, theater: 'north_africa' },
      { longitude: 11, latitude: 35, theater: 'north_africa' },
      { longitude: 12, latitude: 32, theater: 'north_africa' },
      { longitude: 30, latitude: 55, theater: 'eastern_front' },
    ];
    assert.deepEqual(initialMapBounds(africa, ''), claimBounds(africa.slice(0, 3)));
  });

  it('returns the only available box when every claim is in one theater', () => {
    assert.deepEqual(initialMapBounds([lunga, tulagi], ''), claimBounds([lunga, tulagi]));
  });
});
