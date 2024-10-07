from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    # Relationship: One Hero has many HeroPowers
    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')

    # Serialization rules: Exclude 'hero_powers.hero' and 'hero_powers.power' to limit recursion
    serialize_rules = ('-hero_powers', )

    def __repr__(self):
        return f'<Hero {self.id} - {self.super_name}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    # Relationship: One Power has many HeroPowers
    hero_powers = db.relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')

    # Serialization rules: Exclude 'hero_powers.hero' and 'hero_powers.power' to limit recursion
    serialize_rules = ('-hero_powers',)

    # Validation: Description must be present and at least 20 characters long
    @validates('description')
    def validate_description(self, key, description):
        if not description or len(description.strip()) < 20:
            raise ValueError("Description must be at least 20 characters long")
        return description

    def __repr__(self):
        return f'<Power {self.id} - {self.name}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)

    # Relationships
    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')

    # Serialization rules: Include 'hero' and 'power' details, exclude nested 'hero_powers'
    serialize_rules = ('-hero.hero_powers', '-power.hero_powers')

    # Validation: Strength must be one of 'Strong', 'Weak', 'Average'
    @validates('strength')
    def validate_strength(self, key, strength):
        valid_strengths = ['Strong', 'Weak', 'Average']
        if strength not in valid_strengths:
            raise ValueError(f"Strength must be one of {valid_strengths}")
        return strength

    def __repr__(self):
        return f'<HeroPower {self.id} - {self.strength}>'
