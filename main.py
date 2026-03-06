import re
import unittest
import uuid
from datetime import datetime


class UsernameException(Exception):
    pass


class PaymentException(Exception):
    pass


class CreditCardException(Exception):
    pass


class Payment:

    def __init__(self, amount: float, actor: 'User', target: 'User', note: str):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note

    def __str__(self):
        return f"{self.actor.username} paid {self.target.username} ${round(self.amount, 2)} for {self.note}"
 

class Event:
    def __init__(self, message: str):
        self.message = message
        self.timestamp = datetime.now()

class User:

    def __init__(self, username):
        self.credit_card_number = None
        self.balance = 0.0
        self.list_payments = []
        self.list_friends = []
        self.list_feed_events = []

        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException('Username not valid.')


    def retrieve_feed(self) -> list[Payment]:
        return self.list_feed_events
    
    def add_event(self, message: str) -> Event:
        self.list_feed_events.append(Event(message))

    def add_friend(self, new_friend: 'User'):
        self.list_friends.append(new_friend.username)
        new_friend.list_friends.append(self.username)

        self.add_event(f"{self.username} and {new_friend.username} are now friends")
        new_friend.add_event(f"{new_friend.username} and {self.username} are now friends")

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number

        else:
            raise CreditCardException('Invalid credit card number.')

    def pay(self, target: 'User', amount: float, note: str) -> Payment:
        amount = float(amount)
        
        has_enough_balance = self.balance >= amount
        if has_enough_balance:
            payment = self.pay_with_balance(target, amount, note)
        else:
            payment = self.pay_with_card(target, amount, note)
        
        self.list_payments.append(payment)
        target.list_payments.append(payment)

        payment_event = str(payment)
        self.add_event(payment_event)
        target.add_event(payment_event)

        return payment

    def pay_with_card(self, target: 'User', amount: float, note: str) -> Payment:
        amount = float(amount)

        self._validate_pay(target, amount, via_card=True)

        self._charge_credit_card(self.credit_card_number)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def pay_with_balance(self, target: 'User', amount: float, note: str) -> Payment:
        self._validate_pay(target, amount, via_card=False)
        self.balance -= amount
        target.add_to_balance(amount)
        payment = Payment(amount, self, target, note)

        return payment

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        return re.match('^[A-Za-z0-9_\\-]{4,15}$', username)

    def _charge_credit_card(self, credit_card_number):
        # magic method that charges a credit card thru the card processor
        pass
    
    def _validate_pay(self, target: 'User', amount: float, via_card: bool):
        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif via_card and self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')



class MiniVenmo:
    def create_user(self, username, balance, credit_card_number):
        user = User(username)
        user.add_to_balance(balance)
        user.add_credit_card(credit_card_number)
        return user

    def render_feed(self, feed: list[Event]):
        output = ""

        for index, event in enumerate(feed):
            output += f"{index + 1}. {event.message}\n"

        print(output)

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")
 
            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        bobby.add_friend(carol)
        venmo.render_feed(feed)



class TestUser(unittest.TestCase):

    def test_this_works(self):
        with self.assertRaises(UsernameException):
            raise UsernameException()


if __name__ == '__main__':
    # unittest.main()
    mv = MiniVenmo()
    mv.run()