# tt

## Challenge Objectives

MiniVenmo! Imagine that your phone and wallet are trying to have a beautiful baby. In order to make this happen, you must write a social payment app.

Implement a program that will feature users, credit cards, and payment feeds.

### STEP BY STEP:
1. Complete the `MiniVenmo.create_user()` method to allow our application to create new users.

2. Complete the `User.pay()` method to allow users to pay each other. Consider the following: if user A is paying user B, user's A balance should be used if there's enough balance to cover the whole payment, if not, user's A credit card should be charged instead.

3. Venmo has the Feed functionality, that shows the payments that users have been doing in the app. If Bobby paid Carol $5, and then Carol paid Bobby $15, it should look something like this


Bobby paid Carol $5.00 for Coffee
Carol paid Bobby $15.00 for Lunch

Implement the `User.retrieve_activity()` and `MiniVenmo.render_feed()` methods so the MiniVenmo application can render the feed.

4. Now users should be able to add friends. Implement the `User.add_friend()` method to allow users to add friends.

5. Now modify the methods involved in rendering the feed to also show when user's added each other as friends.

## Notes

1. No notes. Pretty straightforward.

2. Used helper methods `pay_with_balance` and `pay_with_card`. Centralized payment validation in `_validate_pay`.

3. Added `list_payments` to `User`. `Payments` are recorded both on actor and target lists. `retrieve_feed` returns this object. `render_feed` displays it as asked.

4. Added `list_friends` to `User`. Similar to `list_payments`, a new friend entry is added on both actor and target.

5. Added `list_feed_events` with a message and timestamp to hold all events for user, from all sources.

### Improvements
