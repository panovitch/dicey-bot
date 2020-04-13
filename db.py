import shelve


class DB:
    def __init__(self, filename=None, user_id=None):
        self.filename = filename or 'main.db'
        self.user_id = user_id or 'test'
        with shelve.open(self.filename) as db:
            if user_id not in db.keys():
                db[self.user_id] = {
                    'saved_rolls': {}
                }

    def save(self, user_data):
        with shelve.open(self.filename) as db:
            db[self.user_id] = user_data

    def load(self):
        with shelve.open(self.filename) as db:
            return db[self.user_id]

    def get_saved_roll(self, roll_name):
        with shelve.open(self.filename) as db:
            try:
                return db[self.user_id]['saved_rolls'][roll_name]
            except KeyError:
                return None

    def get_previous_roll(self):
        with shelve.open(self.filename) as db:
            try:
                return db[self.user_id]['previous_roll']
            except KeyError:
                return None

    def save_previous_roll(self, roll):
        with shelve.open(self.filename, writeback=True) as db:
            db[self.user_id]['previous_roll'] = roll

    def save_roll(self, roll_name, roll):
        with shelve.open(self.filename, writeback=True) as db:
            db[self.user_id]['saved_rolls'][roll_name] = roll

    def get_saved_rolls(self):
        with shelve.open(self.filename) as db:
            return db[self.user_id]['saved_rolls']
