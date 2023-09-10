import requests
import sqlite3
import argparse
import json


class borred_wrap:

    def __init__(self, url, filename):  # stores the url and sqlite database filename
        self.url = url
        self.activ = requests.get(self.url).json()
        self.file = filename

    def borred_get(self):  # performs get on url
        self.activ = requests.get(self.url).json()
        return self.activ

    def borred_save(self):  # saves to sqlite db
        conn = sqlite3.connect(self.file)
        curs = conn.cursor()
        curs.execute("""INSERT INTO
                    activs(activity,type,participants,price,link,key,accessibility)
                                VALUES (?,?,?,?,?,?,?)""", (self.activ["activity"], self.activ["type"], self.activ["participants"],
                                                            self.activ["price"], self.activ["link"], self.activ["key"],
                                                            self.activ["accessibility"],))
        conn.commit()
        conn.close()
        return 1

    def borred_filter(self, typ="type", partc="participants", price_min=0, price_max=2, acc_min=0, acc_max=2):
        # make filters by type, number of participants,
        # price range, and accessibility range
        # should be as: SELECT * from ___ WHERE type = , ...

        conn = sqlite3.connect(self.file)
        curs = conn.cursor()

        select_stat = """SELECT * FROM activs WHERE (type = {} AND participants = {} AND (price BETWEEN {} AND {})
         AND (accessibility BETWEEN {} AND {}));""".format(typ, partc, price_min, price_max, acc_min, acc_max)

        print(select_stat)
        curs.execute(select_stat)
        res = curs.fetchall()
        conn.close()
        return res

    def borred_list(self):
        conn = sqlite3.connect(self.file)
        curs = conn.cursor()
        curs.execute("""SELECT *
        FROM activs 
        LIMIT 5;""")
        res = curs.fetchall()
        conn.close()
        return res


class TerminalError(Exception):
    def __init__(self):
        super().__init__("Wrong command used")


def terminal():
    parser = argparse.ArgumentParser()
    parser.add_argument("com")
    parser.add_argument("--type", type=str, default="social")
    parser.add_argument("--participants", type=int, default="1")
    parser.add_argument("--price_min", type=float, default=0)
    parser.add_argument("--price_max", type=float, default=2)
    parser.add_argument("--accessibility_min", type=float, default=0)
    parser.add_argument("--accessibility_max", type=float, default=2)
    subparsers = parser.add_subparsers()

    parser_a = subparsers.add_parser('list')
    parser_a.add_argument("list")
    return parser


if __name__ == '__main__':
    args = terminal()
    args = vars(args.parse_args())
    bw = borred_wrap("https://www.boredapi.com/api/activity", "bored_activs.db")
    if args["com"] == "new":
        while True:
            print(json.dumps(bw.activ, indent=4))
            if ((bw.activ["type"] == args["type"]) and (bw.activ["participants"] == args["participants"]) and
                    ((bw.activ["price"] <= args['price_max']) and (bw.activ["price"] >= args['price_min'])) and
                    ((bw.activ["accessibility"] <= args['accessibility_max']) and
                     (bw.activ["accessibility"] >= args['accessibility_min']))):
                bw.borred_save()
                print("Found one!")
                break
            else:
                bw.borred_get()
    elif args["com"]=="list":
        print(json.dumps(bw.borred_list(), indent=4))
    else:
        raise TerminalError
