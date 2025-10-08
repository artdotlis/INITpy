from pkg1.sub.sub import MySub
from shared_utils.hello import main


class MyMain:
    """Main class for pkg1.

    This class serves as the entry point for pkg1 functionality.
    It demonstrates how the package can coordinate different
    components (e.g., sub modules and external utilities).
    """

    def method_main(self, inp: str, /) -> None:
        """Print the supplied message.

        Args:
            inp (str): The message to print to stdout.
        """
        print(inp)


def run() -> None:
    """Execute the demo flow of pkg1.

    The function joins a static list of words via :class:`MySub`,
    passes the resulting string to :class:`MyMain`, and finally
    calls the :func:`main` function from ``shared_utils.hello``.
    """
    message = " ".join(MySub().method_sub(["Hello", "world", "!"]))
    MyMain().method_main(message)
    main()


if __name__ == "__main__":
    run()
