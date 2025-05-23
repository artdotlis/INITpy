from pkg1.sub.sub import MySub
from shared_utils.hello import main


class MyMain:
    """_summary_"""

    def method_main(self, inp: str, /) -> None:
        """_summary_

        Args:
            inp (str): _description_
        """
        print(inp)


def run() -> None:
    MyMain().method_main(" ".join(MySub().method_sub(["Hello", "world", "!"])))
    main()


if __name__ == "__main__":
    run()
