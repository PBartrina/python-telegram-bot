#!/usr/bin/env python
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
from datetime import datetime, timedelta, timezone

import pytest

from telegram import MessageEntity, Poll, PollAnswer, PollOption, User
from telegram._utils.datetime import to_timestamp
from telegram.constants import PollType


@pytest.fixture(scope="module")
def poll_option():
    out = PollOption(text=PollOptionSpace.text, voter_count=PollOptionSpace.voter_count)
    out._unfreeze()
    return out


class PollOptionSpace:
    text = "test option"
    voter_count = 3


class TestPollOptionNoReq:
    def test_slot_behaviour(self, poll_option, mro_slots):
        for attr in poll_option.__slots__:
            assert getattr(poll_option, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(poll_option)) == len(set(mro_slots(poll_option))), "duplicate slot"

    def test_de_json(self):
        json_dict = {"text": PollOptionSpace.text, "voter_count": PollOptionSpace.voter_count}
        poll_option = PollOption.de_json(json_dict, None)
        assert poll_option.api_kwargs == {}

        assert poll_option.text == PollOptionSpace.text
        assert poll_option.voter_count == PollOptionSpace.voter_count

    def test_to_dict(self, poll_option):
        poll_option_dict = poll_option.to_dict()

        assert isinstance(poll_option_dict, dict)
        assert poll_option_dict["text"] == poll_option.text
        assert poll_option_dict["voter_count"] == poll_option.voter_count

    def test_equality(self):
        a = PollOption("text", 1)
        b = PollOption("text", 1)
        c = PollOption("text_1", 1)
        d = PollOption("text", 2)
        e = Poll(123, "question", ["O1", "O2"], 1, False, True, Poll.REGULAR, True)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="module")
def poll_answer():
    return PollAnswer(PollAnswerSpace.poll_id, PollAnswerSpace.user, PollAnswerSpace.poll_id)


class PollAnswerSpace:
    poll_id = "id"
    user = User(1, "", False)
    option_ids = [2]


class TestPollAnswerNoReq:
    def test_de_json(self):
        json_dict = {
            "poll_id": PollAnswerSpace.poll_id,
            "user": PollAnswerSpace.user.to_dict(),
            "option_ids": PollAnswerSpace.option_ids,
        }
        poll_answer = PollAnswer.de_json(json_dict, None)
        assert poll_answer.api_kwargs == {}

        assert poll_answer.poll_id == PollAnswerSpace.poll_id
        assert poll_answer.user == PollAnswerSpace.user
        assert poll_answer.option_ids == tuple(PollAnswerSpace.option_ids)

    def test_to_dict(self, poll_answer):
        poll_answer_dict = poll_answer.to_dict()

        assert isinstance(poll_answer_dict, dict)
        assert poll_answer_dict["poll_id"] == poll_answer.poll_id
        assert poll_answer_dict["user"] == poll_answer.user.to_dict()
        assert poll_answer_dict["option_ids"] == list(poll_answer.option_ids)

    def test_equality(self):
        a = PollAnswer(123, PollAnswerSpace.user, [2])
        b = PollAnswer(123, User(1, "first", False), [2])
        c = PollAnswer(123, PollAnswerSpace.user, [1, 2])
        d = PollAnswer(456, PollAnswerSpace.user, [2])
        e = PollOption("Text", 1)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="module")
def poll():
    poll = Poll(
        PollSpace.id_,
        PollSpace.question,
        PollSpace.options,
        PollSpace.total_voter_count,
        PollSpace.is_closed,
        PollSpace.is_anonymous,
        PollSpace.type,
        PollSpace.allows_multiple_answers,
        explanation=PollSpace.explanation,
        explanation_entities=PollSpace.explanation_entities,
        open_period=PollSpace.open_period,
        close_date=PollSpace.close_date,
    )
    poll._unfreeze()
    return poll


class PollSpace:
    id_ = "id"
    question = "Test?"
    options = [PollOption("test", 10), PollOption("test2", 11)]
    total_voter_count = 0
    is_closed = True
    is_anonymous = False
    type = Poll.REGULAR
    allows_multiple_answers = True
    explanation = (
        b"\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467"
        b"\\u200d\\U0001f467\\U0001f431http://google.com"
    ).decode("unicode-escape")
    explanation_entities = [MessageEntity(13, 17, MessageEntity.URL)]
    open_period = 42
    close_date = datetime.now(timezone.utc)


class TestPollNoReq:
    def test_de_json(self, bot):
        json_dict = {
            "id": PollSpace.id_,
            "question": PollSpace.question,
            "options": [o.to_dict() for o in PollSpace.options],
            "total_voter_count": PollSpace.total_voter_count,
            "is_closed": PollSpace.is_closed,
            "is_anonymous": PollSpace.is_anonymous,
            "type": PollSpace.type,
            "allows_multiple_answers": PollSpace.allows_multiple_answers,
            "explanation": PollSpace.explanation,
            "explanation_entities": [PollSpace.explanation_entities[0].to_dict()],
            "open_period": PollSpace.open_period,
            "close_date": to_timestamp(PollSpace.close_date),
        }
        poll = Poll.de_json(json_dict, bot)
        assert poll.api_kwargs == {}

        assert poll.id == PollSpace.id_
        assert poll.question == PollSpace.question
        assert poll.options == tuple(PollSpace.options)
        assert poll.options[0].text == PollSpace.options[0].text
        assert poll.options[0].voter_count == PollSpace.options[0].voter_count
        assert poll.options[1].text == PollSpace.options[1].text
        assert poll.options[1].voter_count == PollSpace.options[1].voter_count
        assert poll.total_voter_count == PollSpace.total_voter_count
        assert poll.is_closed == PollSpace.is_closed
        assert poll.is_anonymous == PollSpace.is_anonymous
        assert poll.type == PollSpace.type
        assert poll.allows_multiple_answers == PollSpace.allows_multiple_answers
        assert poll.explanation == PollSpace.explanation
        assert poll.explanation_entities == tuple(PollSpace.explanation_entities)
        assert poll.open_period == PollSpace.open_period
        assert abs(poll.close_date - PollSpace.close_date) < timedelta(seconds=1)
        assert to_timestamp(poll.close_date) == to_timestamp(PollSpace.close_date)

    def test_to_dict(self, poll):
        poll_dict = poll.to_dict()

        assert isinstance(poll_dict, dict)
        assert poll_dict["id"] == poll.id
        assert poll_dict["question"] == poll.question
        assert poll_dict["options"] == [o.to_dict() for o in poll.options]
        assert poll_dict["total_voter_count"] == poll.total_voter_count
        assert poll_dict["is_closed"] == poll.is_closed
        assert poll_dict["is_anonymous"] == poll.is_anonymous
        assert poll_dict["type"] == poll.type
        assert poll_dict["allows_multiple_answers"] == poll.allows_multiple_answers
        assert poll_dict["explanation"] == poll.explanation
        assert poll_dict["explanation_entities"] == [poll.explanation_entities[0].to_dict()]
        assert poll_dict["open_period"] == poll.open_period
        assert poll_dict["close_date"] == to_timestamp(poll.close_date)

    def test_equality(self):
        a = Poll(123, "question", ["O1", "O2"], 1, False, True, Poll.REGULAR, True)
        b = Poll(123, "question", ["o1", "o2"], 1, True, False, Poll.REGULAR, True)
        c = Poll(456, "question", ["o1", "o2"], 1, True, False, Poll.REGULAR, True)
        d = PollOption("Text", 1)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

    def test_enum_init(self):
        poll = Poll(
            type="foo",
            id="id",
            question="question",
            options=[],
            total_voter_count=0,
            is_closed=False,
            is_anonymous=False,
            allows_multiple_answers=False,
        )
        assert poll.type == "foo"
        poll = Poll(
            type=PollType.QUIZ,
            id="id",
            question="question",
            options=[],
            total_voter_count=0,
            is_closed=False,
            is_anonymous=False,
            allows_multiple_answers=False,
        )
        assert poll.type is PollType.QUIZ

    def test_parse_entity(self, poll):
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        poll.explanation_entities = [entity]

        assert poll.parse_explanation_entity(entity) == "http://google.com"

        with pytest.raises(RuntimeError, match="Poll has no"):
            Poll(
                "id",
                "question",
                [PollOption("text", voter_count=0)],
                total_voter_count=0,
                is_closed=False,
                is_anonymous=False,
                type=Poll.QUIZ,
                allows_multiple_answers=False,
            ).parse_explanation_entity(entity)

    def test_parse_entities(self, poll):
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        entity_2 = MessageEntity(type=MessageEntity.BOLD, offset=13, length=1)
        poll.explanation_entities = [entity_2, entity]

        assert poll.parse_explanation_entities(MessageEntity.URL) == {entity: "http://google.com"}
        assert poll.parse_explanation_entities() == {entity: "http://google.com", entity_2: "h"}
