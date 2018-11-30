import asyncio
import random
import re
from collections import namedtuple
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from operator import attrgetter
from typing import Callable

from config import settings

Food = namedtuple('Food', ['name', 'count', 'command'])


@dataclass()
class User:
    ACTIONS_MAPPING = {
        'pip_boy': '📟Пип-бой',
        'action': '🔎Дeйствие',
        'attack': '⚔️Дать отпор',
        'my_food': '/myfood',
        'return': '⛺️Вернуться',
        'return_confirm': 'Вернуться в лагерь',
        'wasteland': '👣Пустошь',
        'step': '👣Идти дaльше',
    }
    _send: Callable
    name: str = ''
    hp_min: int = 0
    hp_max: int = 0
    hunger: int = 0
    stamina_min: int = 0
    stamina_max: int = 0
    location: str = ''
    distance: int = 0
    last_message: datetime = datetime.utcnow()
    available_food: list = field(default_factory=list)

    def __post_init__(self):
        if not callable(self._send):
            raise AttributeError(f'{self._send} must be callable')

    def __repr__(self):
        return f'User({self.name}, ' \
            f'hp={self.hp_min}/{self.hp_max} ' \
            f'hunger={self.hunger}, ' \
            f'stamina={self.stamina_min}/{self.stamina_max}, ' \
            f'location={self.location}, ' \
            f'distance={self.distance}, ' \
            f'last_message={self.last_message.strftime("%Y-%m-%d-%H:%M:%S")})'

    @property
    def is_hungry(self):
        return self.hunger > settings.HUNGER_LEVEL

    @property
    def in_camp(self):
        return self.location == 'Лагерь'

    async def update_info(self, message):
        self.name = re.search(r'\n\w+\n[^👥Фракция]?', message)[0].strip()
        hp = re.findall(r'[\n]❤️Здоровье:\s*([^\n\r]*)', message)[0]
        self.hp_min, self.hp_max = map(int, hp.split('/'))
        self.hunger = int(re.findall(r'[\n]🍗Голод:\s*([^\n\r][^%]*)', message)[0])
        stamina = re.findall(r'[\n]🔋Выносливость:\s*([^\n\r]*)', message)[0]
        self.stamina_min, self.stamina_max = map(int, stamina.split('/'))
        self.location = re.findall(r'[\n]🔥Локация:\s*([^\n\r]*)', message)[0]
        self.distance = int(re.findall(r'[\n]👣Расстояние:\s*([^\n\r]*)', message)[0])

    async def update_stats(self, message):
        hp = re.findall(r'[❤]️(\d{1,4}/\d{1,4})', message)[0]
        self.hp_min, self.hp_max = map(int, hp.split('/'))
        self.hunger = int(re.findall(r'[\s]🍗([^\n\r][^%]*)', message)[0])
        stamina = re.findall(r'[\s]🔋(\d{1,2}/\d{1,2})', message)[0]
        self.stamina_min, self.stamina_max = map(int, stamina.split('/'))
        self.distance = int(re.findall(r'[\s]👣\s*([^\n\r][^км]*)', message)[0])
        if message[0] != '❤':
            self.location = re.findall(r'^.*[^\n❤️]', message)[0]

    async def update_food(self, message):
        food = re.split(r'Вещества', re.split(r'Пища', message)[1])[0]
        food = filter(None, re.split(r'\n', food))
        for item in food:
            name = re.findall(r'\s(.*?)[(|/]', item)[0].strip()
            try:
                count = int(re.findall(r'\((\d+)\)', item)[0])
            except IndexError:
                count = 1
            command = re.findall(r'/.*$', item)[0]
            self.available_food.append(
                Food(name, count, command)
            )

    async def update_hungry_level(self, message):
        self.hunger = int(re.findall(r'[:\s]\d+[^%]', message)[0])

    async def eat(self, logger):
        try:
            self.available_food.sort(key=attrgetter('count'), reverse=True)
            food = self.available_food.pop(0)
        except IndexError:
            logger.info('Searching food...')
            await self.my_food()
        else:
            if food.count > 1:
                count = food.count - 1
                food = food._replace(count=count)
                self.available_food.append(food)
                logger.info(f'Eating {food.name}')
                await self.send(food.command)

    async def send(self, command):
        await asyncio.sleep(random.randint(2, 5))
        await self._send(command)

    async def attack(self):
        await self.send(self.ACTIONS_MAPPING['attack'])

    async def go_ahead(self):
        if self.in_camp:
            await self.send(self.ACTIONS_MAPPING['wasteland'])
        else:
            await self.send(self.ACTIONS_MAPPING['step'])

    async def my_food(self):
        await self.send(self.ACTIONS_MAPPING['my_food'])

    async def go_home(self):
        await self.send(self.ACTIONS_MAPPING['return'])

    async def confirm(self):
        await self.send(self.ACTIONS_MAPPING['return_confirm'])

    async def ping(self):
        await self.send(self.ACTIONS_MAPPING['pip_boy'])
