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

    def setUp(self):
        self.user = User("Bobby")
        self.user.add_to_balance(5)
        self.user.add_credit_card("4111111111111111")

        self.target = User("Carol")
        self.target.add_to_balance(10)
        self.target.add_credit_card("4242424242424242")

    def test_valid_username(self):
        user = User("Test_User-1")
        self.assertEqual(user.username, "Test_User-1")

    def test_username_too_short(self):
        with self.assertRaises(UsernameException):
            User("abc")

    def test_username_too_long(self):
        with self.assertRaises(UsernameException):
            User("a" * 16)

    def test_username_invalid_characters(self):
        with self.assertRaises(UsernameException):
            User("user@name!")

    def test_add_valid_credit_card(self):
        user = User("NoCCUser")
        user.add_credit_card("4242424242424242")
        self.assertEqual(user.credit_card_number, "4242424242424242")

    def test_add_invalid_credit_card(self):
        user = User("NoCCUser")
        with self.assertRaises(CreditCardException):
            user.add_credit_card("0000000000000000")

    def test_add_duplicate_credit_card(self):
        with self.assertRaises(CreditCardException):
            self.user.add_credit_card("4242424242424242")

    def test_add_to_balance(self):
        self.user.add_to_balance(10)
        self.assertEqual(self.user.balance, 15)

    def test_add_friend(self):
        self.user.add_friend(self.target)
        self.assertIn(self.target.username, self.user.list_friends)
        self.assertIn(self.user.username, self.target.list_friends)

    def test_add_friend_creates_feed_events(self):
        self.user.add_friend(self.target)
        self.assertEqual(len(self.user.list_feed_events), 1)
        self.assertEqual(len(self.target.list_feed_events), 1)

    def test_retrieve_feed_empty(self):
        self.assertEqual(self.user.retrieve_feed(), [])

    def test_add_event(self):
        self.user.add_event("test message")
        self.assertEqual(len(self.user.list_feed_events), 1)
        self.assertEqual(self.user.list_feed_events[0].message, "test message")

    def test_pay_self_raises(self):
        with self.assertRaises(PaymentException):
            self.user.pay(self.user, 1, "Self pay")

    def test_pay_zero_amount_raises(self):
        with self.assertRaises(PaymentException):
            self.user.pay(self.target, 0, "Zero")

    def test_pay_negative_amount_raises(self):
        with self.assertRaises(PaymentException):
            self.user.pay(self.target, -5, "Negative")

    def test_pay_with_card_no_card_raises(self):
        user_no_card = User("NoCard")
        with self.assertRaises(PaymentException):
            user_no_card.pay(self.target, 1, "No card")

    def test_pay_with_balance(self):
        payment = self.user.pay(self.target, 5, "Coffee")
        self.assertEqual(self.user.balance, 0)
        self.assertEqual(self.target.balance, 15)
        self.assertEqual(payment.amount, 5)

    def test_pay_with_card(self):
        payment = self.user.pay(self.target, 10, "Lunch")
        self.assertEqual(self.user.balance, 5)
        self.assertEqual(self.target.balance, 20)
        self.assertEqual(payment.amount, 10)

    def test_pay_adds_to_both_payment_lists(self):
        self.user.pay(self.target, 1, "Test")
        self.assertEqual(len(self.user.list_payments), 1)
        self.assertEqual(len(self.target.list_payments), 1)

    def test_pay_adds_feed_events(self):
        self.user.pay(self.target, 1, "Test")
        self.assertEqual(len(self.user.list_feed_events), 1)
        self.assertEqual(len(self.target.list_feed_events), 1)

    def test_payment_str(self):
        payment = Payment(5, self.user, self.target, "Coffee")
        self.assertEqual(str(payment), "Bobby paid Carol $5.0 for Coffee")


class TestMiniVenmo(unittest.TestCase):

    def test_create_user(self):
        venmo = MiniVenmo()
        user = venmo.create_user("TestUser", 10, "4111111111111111")
        self.assertEqual(user.username, "TestUser")
        self.assertEqual(user.balance, 10)
        self.assertEqual(user.credit_card_number, "4111111111111111")

    def test_render_feed(self, ):
        venmo = MiniVenmo()
        user = venmo.create_user("TestUser", 10, "4111111111111111")
        target = venmo.create_user("Target", 5, "4242424242424242")
        user.pay(target, 1.00, "Coffee")
        feed = user.retrieve_feed()
        venmo.render_feed(feed) 

if __name__ == '__main__':
    unittest.main()
    # mv = MiniVenmo()
    # mv.run()