# Snooker Rules Summary for This App

This app models a standard two-player snooker frame with the core scoring and turn-order rules, plus lightweight match tracking across frames.

## Scoring values

- Red = 1
- Yellow = 2
- Green = 3
- Brown = 4
- Blue = 5
- Pink = 6
- Black = 7

## Frame flow

### 1. Reds-and-colours phase

While reds remain on the table:
- the ball on is **a red** at the start of a visit
- if a player pots a red, they score 1 per red potted
- after a legal red, the next ball on is **any one colour**
- if a player pots a legal colour during this phase, it scores its face value and is **re-spotted**
- the next ball on becomes red again

Notes:
- multiple reds may be potted in one legal shot
- only one nominated colour is scored after a red

### 2. Transition after the final red

After the last red is potted:
- the striker still gets one colour next
- that colour scores normally
- after that, the frame enters the clearance phase

### 3. Colours clearance phase

Once no reds remain and the post-final-red colour chance is resolved:
- colours must be potted in order:
  - yellow
  - green
  - brown
  - blue
  - pink
  - black
- during this phase, colours are **not re-spotted**

## Visits, breaks, and turns

- a break is the points scored in one visit
- a visit ends when the player misses, fouls, or the frame ends
- a foul ends the break immediately
- a miss with no score also ends the break

## Fouls

This app supports manual foul entry with typical penalty values:
- 4
- 5
- 6
- 7

The foul points are awarded to the opponent.

This matches the practical scoring behavior, though the app does not yet auto-calculate every foul type from shot geometry or ball-contact details.

## Snookers required pressure

The app computes:
- current lead
- points remaining on the table
- whether the trailing player needs snookers

If the lead is greater than the points remaining, the trailer needs penalty points from fouls to catch up.

## End of frame

A frame is complete when:
- all reds are gone, and
- all six colours have been cleared in order

The higher score wins.

If scores are level after all colours are gone, the app can start a **re-spotted black** decider:
- only the black is on
- the next score wins the frame
- potting the black wins
- fouling on the black concedes 7 and loses the frame
- a miss simply passes the turn

## Lightweight match tracking

The app also keeps a simple running match score:
- configurable **best-of** match length
- running **frames won** for each player
- a **start next frame + record winner** action after a completed frame
- local persistence for both the current frame and current match score

This is intended for practical table-side use, not as a full historical match database.

## What is intentionally not yet modeled

To keep the UI friendly, this version does **not** fully simulate:
- ball positions
- touching ball situations
- free balls
- exact foul inference from first contact
- re-spot placement conflicts
- referee-called situations like miss warnings
- concession handling
- full frame-by-frame match history or archival review
- a dedicated match-domain rules engine separate from the UI state

It focuses on accurate frame scoring flow, turn order, foul scoring, scoreboard usability, practical persistence, and simple multi-frame match progress for a local table-side app.
