from topic_fetcher import GENRES, _entity, _same_event

def test_three_sports_genres():
    assert len(GENRES) == 3

def test_entity():
    assert _entity("Virat Kohli scores another century") == "Virat Kohli"

def test_same_event():
    a={"title":"Virat Kohli scores another century","url":"https://a.com/1"}
    b={"title":"Virat Kohli hits century for India","url":"https://b.com/2"}
    assert _same_event(a,b)
