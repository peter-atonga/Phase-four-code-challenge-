import pytest
from app import app
from models import db, Hero, Power, HeroPower
from faker import Faker


class TestPower:
    '''Class Power in models.py'''

    def test_description_valid(self):
        '''requires description at least 20 letters.'''

        with app.app_context():
            with pytest.raises(ValueError):
                power = Power(name=Faker().name(),
                              description="flies")
                db.session.add(power)
                db.session.commit()


class TestHeroPower:
    '''Class HeroPower in models.py'''

    def test_strength_valid(self):
        '''requires strength to be Strong, Weak, Average.'''

        with app.app_context():
            with pytest.raises(ValueError):
                fake = Faker()
                hero = Hero(name=fake.name(), super_name=fake.name())
                power = Power(name=fake.name(), description=fake.sentence())
                db.session.add_all([hero, power])
                db.session.commit()

                hero_power = HeroPower(
                    hero_id=hero.id, power_id=power.id, strength='Super Strong')
                db.session.add(hero_power)
                db.session.commit()
