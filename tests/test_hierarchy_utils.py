from hierarchy_utils import __version__ as hu_version
from hierarchy_utils import *
from collections import OrderedDict
from copy import deepcopy

teams = OrderedDict({"compile-day": "monday",
                          "compile-secret": "SECRET!",
                          "nhl": [{"team": "stars"  , "players": 10, "pos": ["l", "r", "c"]},
                                  {"team": "bruins" , "players": 30 },
                                  {"team": "preds"  , "players": 90 }],
                          "nba": [{"team": "mavs"   , "players": -9, "details": [{"who": "bill", "pos": ["r", "c", "l"]},
                                                                                 {"who": "ted", "pos": ["d"]},
                                                                                 {"who": "fred"}]},
                                  {"team": "bucks"  , "players": 3 , "details": [{"who": "ken" , "pos": ["c"]}]}],})

more_fake_data = {'Coach': {'Name': {'Title': 'Mr', 'Surname': 'one', 'GivenName': 'person'},
                           'DOB': '1984-01-01',
                           'Gender': 'F'},
             'TeamPlayers': [{'Name': {'Title': 'Mr', 'Surname': 'one', 'GivenName': 'person'},
                                 'DOB': '1984-01-01',
                                 'jerseyDetails': [{'JerseyNumber': '#1', 'Size': 'Large'},
                                                   {'JerseyNumber': '1'  , 'Size': 'Small'}],
                                 'Gender': 'M'},
                                {'Name': {'Title': 'Mr', 'Surname': 'two', 'GivenName': 'person'},
                                 'DOB': '1901-01-01',
                                 'jerseyDetails': [{'JerseyNumber': 'ID2', 'Size': 'Large'}],
                                 'Gender': 'F'}
             ],
             'ExtraData': [{'Name': 'LikesCake'   , 'Value': 'true'}      ,
                           {'Name': 'HasTwin'     , 'Value': 'true'}      ,
                           {'Name': 'EnjoysTwin'  , 'Value': 'false'}     ,
                           {'Name': 'FavCity'     , 'Value': 'Dallas'} ,
                           {'Name': 'HasChildren' , 'Value': 'false'}     ,
                           {'Name': 'MathGrade'   , 'Value': 'A'}         ,
                           {'Name': 'US-State'    , 'Value': 'CT'}        ,
                           {'Name': 'Date'        , 'Value': '2019-01-01'}]}


def test_version():
    assert hu_version == '0.1.1'


def test_path_switchers():
   assert  ['root', 0, 'thing',2] == hp_to_list('/root/0/thing/2')
   assert  '/root/0/thing/2' == list_to_hp(['root', 0, 'thing',2])


def test_get_in_usage():
    #Simple Examples:

    assert get_in_hp("/a"     ,  {"a": 33})                == 33
    assert get_in_hp("/a/b/c" ,  {"a": {"b": {"c": 99 }}}) == 99

    #Examples - Stuctures with Lists:

    teams = {"nhl": [{"team": "stars"  , "players": 10, "pos": ["l", "r", "c"]},
                     {"team": "bruins" , "players": 30 },
                     {"team": "preds"  , "players": 90 }],
             "nba": [{"team": "mavs"   , "players": -9, "details": [{"who": "bill", "pos": ["r", "c", "l"]},
                                                                    {"who": "ted", "pos": ["d"]},
                                                                    {"who": "fred"}]},
                     {"team": "bucks"  , "players": 3 , "details": [{"who": "ken" , "pos": ["c"]}]}],}


    assert get_in_hp("/nhl/1/team",  teams) == "bruins"

    assert get_in_hp("/nhl/2/team",  teams) == "preds"

    # You  could get back a dict
    assert get_in_hp("/nhl/1",  teams)      == {'team': 'bruins', 'players': 30}

    # or get back a list
    assert get_in_hp("/nhl/0/pos",  teams)      == ["l", "r", "c"]

    # Examples - Extracting Wildcards (all data in a list)
    assert get_in_hp("/nhl/*/team", teams) == ["stars", "bruins", "preds"]

    # If a list has two wildcards, it gets interesting:
    # notice the nesting, the record has three players, the second one.
    assert get_in_hp( "/nba/*/details/*/who", teams) == [['bill', 'ted', 'fred'], ['ken']]

    # deep nesting... notice how the structure of the output mirrors the input.
    assert get_in_hp( "/nba/*/details/*/pos/*/", teams) == [[['r', 'c', 'l'], ['d'], None], [['c']]]

    # If you want to flatten the deep nesting in the output, there is a utility
    # function called `flatten_recur`:
    assert flatten_recur(get_in_hp("/nba/*/details/*/pos/*/", teams)) == ['r', 'c', 'l', 'd', None, 'c']


def test_get_in_hp_atomic():
    assert get_in_hp('/Coach/Name/GivenName' , more_fake_data) == 'person'
    assert get_in_hp('/Coach/Name/Surname'   , more_fake_data) == 'one'
    assert get_in_hp('/Coach/DOB'      , more_fake_data) == '1984-01-01'


def test_get_in_hp_integers():
    "test for wildcards in the spec identifier.  Should return a list of results."
    "test for wildcards in the spec identifier.  Should return a list of results."
    assert    get_in_hp('/TeamPlayers/0/Name/GivenName' , more_fake_data) == 'person';
    assert    get_in_hp('/TeamPlayers/0/Name/Surname'   , more_fake_data) == 'one';
    assert    get_in_hp('/TeamPlayers/0/DOB'      , more_fake_data) == '1984-01-01';
    assert    get_in_hp('/ExtraData/0/Name'           , more_fake_data) == 'LikesCake';
    assert    get_in_hp('/ExtraData/0/Value'          , more_fake_data) == 'true';

    assert    get_in_hp('/TeamPlayers/1/Name/GivenName' , more_fake_data) == 'person';
    assert    get_in_hp('/TeamPlayers/1/Name/Surname'   , more_fake_data) == 'two';
    assert    get_in_hp('/TeamPlayers/1/DOB'      , more_fake_data) == '1901-01-01';

    assert    get_in_hp('/ExtraData/2/Name'           , more_fake_data) == 'EnjoysTwin';
    assert    get_in_hp('/ExtraData/2/Value'          , more_fake_data) == 'false';


def test_get_in_hp_stars_single():
    "test for wildcards in the spec identifier.  Should return a list of results."
    assert get_in_hp('/ExtraData/*/Name', more_fake_data) == ['LikesCake',
                                                                      'HasTwin',
                                                                      'EnjoysTwin',
                                                                      'FavCity',
                                                                      'HasChildren',
                                                                      'MathGrade',
                                                                      'US-State',
                                                                      'Date']

    assert get_in_hp('/TeamPlayers/*/Name/GivenName' , more_fake_data) == ['person', 'person']
    assert get_in_hp('/TeamPlayers/*/Name/Surname'   , more_fake_data) == ['one', 'two']
    assert get_in_hp('/TeamPlayers/*/DOB'      , more_fake_data) == ['1984-01-01', '1901-01-01']


def test_get_in_hp_stars_multiple():
    "test for wildcards in the spec identifier.  Should return a list of results."
    assert get_in_hp('/TeamPlayers/*/jerseyDetails/*/JerseyNumber' , more_fake_data) == [["#1", "1"], ["ID2"]]
    assert get_in_hp('/TeamPlayers/*/jerseyDetails/*/Size'   , more_fake_data) == [["Large", "Small"], ["Large"]]


def test_my_assoc_in_coll():
    td1 = deepcopy(teams)
    assert assoc_in_coll(td1,  ['compile-secret'], 'not-secret.' ) == \
        {"compile-day": "monday",
         "compile-secret": "not-secret.",
         "nhl": [{"team": "stars"  , "players": 10, "pos": ["l", "r", "c"]},
                 {"team": "bruins" , "players": 30 },
                 {"team": "preds"  , "players": 90 }],
         "nba": [{"team": "mavs"   , "players": -9, "details": [{"who": "bill", "pos": ["r", "c", "l"]},
                                                                {"who": "ted", "pos": ["d"]},
                                                                {"who": "fred"}]},
                 {"team": "bucks"  , "players": 3 , "details": [{"who": "ken" , "pos": ["c"]}]}]}

    assert assoc_in_coll(td1,  ['nhl', 0, 'players'], 1976 ) == \
        {"compile-day": "monday",
         "compile-secret": "SECRET!",
         "nhl": [{"team": "stars"  , "players": 1976, "pos": ["l", "r", "c"]},
                 {"team": "bruins" , "players": 30 },
                 {"team": "preds"  , "players": 90 }],
         "nba": [{"team": "mavs"   , "players": -9, "details": [{"who": "bill", "pos": ["r", "c", "l"]},
                                                                {"who": "ted", "pos": ["d"]},
                                                                {"who": "fred"}]},
                 {"team": "bucks"  , "players": 3 , "details": [{"who": "ken" , "pos": ["c"]}]}]}

    nba_teams = {"nba": [{"team": "mavs",
                         "players": -9,
                         "details": [{"who": "bill", "pos": ["r", "c", "l"]},
                                     {"who": "coach ted", "pos": ["coach"]},
                                     {"who": "fred"}]},]}

    new_coach = {"nba": [{"team": "mavs",
                         "players": -9,
                         "details": [{"who": "bill", "pos": ["r", "c", "l"]},
                                     {"who": "new coach!", "pos": ["coach"]},
                                     {"who": "fred"}]},]}

    assert assoc_in_coll(nba_teams, ['nba', 0, 'details', 1, 'who'], "new coach!") == new_coach


def test_my_assoc_in_hp():
    td1 = deepcopy(teams)
   
    assert assoc_in_hp(td1,  '/compile-secret', 'not-secret.' ) == \
        {"compile-day": "monday",
         "compile-secret": "not-secret.",
         "nhl": [{"team": "stars"  , "players": 10, "pos": ["l", "r", "c"]},
                 {"team": "bruins" , "players": 30 },
                 {"team": "preds"  , "players": 90 }],
         "nba": [{"team": "mavs"   , "players": -9, "details": [{"who": "bill", "pos": ["r", "c", "l"]},
                                                                {"who": "ted", "pos": ["d"]},
                                                                {"who": "fred"}]},
                 {"team": "bucks"  , "players": 3 , "details": [{"who": "ken" , "pos": ["c"]}]}]}


    assert assoc_in_hp(td1,  '/nhl/0/players', 1976 ) == \
        {"compile-day": "monday",
         "compile-secret": "SECRET!",
         "nhl": [{"team": "stars"  , "players": 1976, "pos": ["l", "r", "c"]},
                 {"team": "bruins" , "players": 30 },
                 {"team": "preds"  , "players": 90 }],
         "nba": [{"team": "mavs"   , "players": -9, "details": [{"who": "bill", "pos": ["r", "c", "l"]},
                                                                {"who": "ted", "pos": ["d"]},
                                                                {"who": "fred"}]},
                 {"team": "bucks"  , "players": 3 , "details": [{"who": "ken" , "pos": ["c"]}]}]}

    nba_teams = {"nba": [{"team": "mavs",
                         "players": -9,
                         "details": [{"who": "bill", "pos": ["r", "c", "l"]},
                                     {"who": "coach ted", "pos": ["coach"]},
                                     {"who": "fred"}]},]}

    new_coach = {"nba": [{"team": "mavs",
                         "players": -9,
                         "details": [{"who": "bill", "pos": ["r", "c", "l"]},
                                     {"who": "new coach!", "pos": ["coach"]},
                                     {"who": "fred"}]},]}

    assert assoc_in_hp(nba_teams, '/nba/0/details/1/who', "new coach!") == new_coach


def test_update_in_hp():

    my_fn = lambda x: x + 1

    assert update_in_hp({"nhl":[{"team": "stars"  , "players": 10},
                                {"team": "preds"  , "players": 90}]},
                        "/nhl/0/players/",
                        my_fn) == {"nhl":[{"team": "stars"  , "players": 11},
                                                     {"team": "preds"  , "players": 90}]}, "Test single Path in list update."

    assert update_in_hp({"nhl":[{"team": "stars"  , "players": 10},
                                {"team": "preds"  , "players": 90}]},
                        "/nhl/*/players/",
                        my_fn, default=0) == {"nhl":[{"team": "stars"  , "players": 11},
                                                     {"team": "preds"  , "players": 91}]}, "Test Wildcard path update."

    assert update_in_hp({"nhl":[{"team": "stars"  , "players": 10},
                                {"team": "bruins" },
                                {"team": "preds"  , "players": 90}]},
                        "/nhl/*/players/",
                        my_fn, default=0) == {"nhl":[{"team": "stars"  , "players": 11},
                                                     {"team": "bruins", "players": 1 },
                                                     {"team": "preds"  , "players": 91}]}, "Test Wildcard path update."

    def ten_percent_raise(salary):
        if salary:
            return salary * 1.10
        else:
            # If they don't have a salary they own us money.
            return -40


    assert update_in_hp({"payroll": [{"player": "bill" , "salary": 10, },
                              {"player": "ted"  , "salary": 30, },
                              {"player": "ned"  , "salary": 20, },
                              {"player": "fred" ,               },]},
                 "/payroll/*/salary",
                 ten_percent_raise) == {'payroll': [{'player': 'bill', 'salary': 11.0},
                                                    {'player': 'ted', 'salary': 33.0},
                                                    {'player': 'ned', 'salary': 22.0},
                                                    {'player': 'fred', 'salary': -40}]}


    assert update_in_hp({"payroll": [{"team": "stars", "players": [{"player": "bill" , "salary": 10, },
                                                                   {"player": "ted"  , "salary": 30, },
                                                                   {"player": "ned"  , "salary": 20, },
                                                                   {"player": "fred" ,               },]},
                                     {"team": "preds", "players": [{"player": "ken"  , "salary":  5, },
                                                                   {"player": "jen"  , "salary":  8, },
                                                                   {"player": "ben"  , "salary":  9, },
                                                                   {"player": "len"  ,               },]}]},
                        "/payroll/*/players/*/salary", # payroll for all teams, all players, salary
                        ten_percent_raise) == {'payroll': [{'players': [{'player': 'bill', 'salary': 11.0},
                                                                        {'player': 'ted', 'salary': 33.0},
                                                                        {'player': 'ned', 'salary': 22.0},
                                                                        {'player': 'fred', 'salary': -40}],
                                                            'team': 'stars'},
                                                           {'players': [{'player': 'ken', 'salary': 5.5},
                                                                        {'player': 'jen', 'salary': 8.8},
                                                                        {'player': 'ben', 'salary': 9.9},
                                                                        {'player': 'len', 'salary': -40}],
                                                            'team': 'preds'}]}


