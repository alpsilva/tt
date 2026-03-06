import unittest

from exceptions import UsernameException, PaymentException, CreditCardException
from payment import Payment
from event import Event
from user import User

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