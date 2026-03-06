import re

from exceptions import UsernameException, PaymentException, CreditCardException
from payment import Payment
from event import Event


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
