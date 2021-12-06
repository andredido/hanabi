# HANABI
### Andrea Di Domenico s287639
Computational Intelligence A.A. 2021/2022 - Politecnico di Torino

## Game Components
50 fireworks cards in five colors (red, yellow, green, blue, white)
10 cards per color with the values 1, 1, 1, 2, 2, 3, 3, 4, 4, 5
10 colorful fireworks cards with values of 1, 1, 1, 2, 2, 3, 3, 4, 4, 5
8 Note tokens (+ 1 spare)
3 Storm tokens

## Object of the Game
Hanabi is a cooperative game, meaning all players play together as a team. The players have to play the fireworks cards sorted by colors and numbers.

However, they see their own hand cards not, and so everyone needs the advice of his fellow players. The more cards the players play correctly, the more points they receive when the game ends.

## Gameplay
Play proceeds clockwise. On a player's turn, he must perform exactly one of the following:

I. Give a hint or
II. Discard a card or
III. Play a card.
The player has to choose an action. A player may not pass.

Important: Players are not allowed to give hints or suggestions on other players' turns.

### I. Give a hint
To give a hint one Note token must be flipped from its white side to its black side. If there are no Note tokens white-side-up then a player may not choose the Give a hint action. Now the player gives a teammate a hint. He has one of two options:

#### Color Hint
The player chooses a color and indicates to his/her teammate which of their hand cards match the chosen color by pointing at the cards. Important: The player must indicate all cards of that color in their teammate's hand!

Example: "You have two yellow cards, here and here". Indicating that a player has no cards of a particular color is allowed!

Example: "You have no blue cards".

#### Value Hint
The player chooses a number value and gives a teammate a hint in the exact same fashion as a Color Hint.

Example: "You have a 5, here".

Example: "You have no Twos"

### II. Discard a card
To discard a card one Note token must be flipped from its black side to its white side. If there are no Note tokens black-side-up then a player may not choose the Discard a card action.

Now the player discards one card from their hand (without looking at the fronts of their hand cards) and discards it face-up in the discard pile near the draw deck. The player then draws another card into their hand in the same fashion as their original card hands, never looking at the front.

### III. Play a card
By playing out cards the fireworks are created in the middle of the table. The player takes one card from his hand and places it face up in the middle of the table. Two things can happen:

The card can be played correctly
The player places the card face up so that it extends a current firework or starts a new firework.

The card cannot be played correctly
The gods are angry with this error and send a flash from the sky. The player turns a Storm tile lightning-side-up. The incorrect card is discarded to the discard pile near the draw deck.

The player then draws another card into their hand in the same fashion as their original card hands, never looking at the front.

## The Fireworks
The fireworks will be in the middle of the table and are designed in five different colors. For each color an ascending series with numerical values from 1 to 5 is formed. A firework must start with the number 1 and each card played to a firework must increment the previously played card by one. A firework may not contain more than one card of each value.

## Bonus
When a player completes a firework by correctly playing a 5 card then the players receive a bonus. One Note token is turned from black side to white side up. If all tokens are already white-side-up then no bonus is received. Play then passes to the next player (clockwise).

## Technics
1) Discard your oldest card
