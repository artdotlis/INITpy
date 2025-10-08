class MySub:
    """Utility helper that simply echoes a list of strings.

    This lightweight class demonstrates how a sub-package can expose
    small building blocks that other parts of the application (or
    external consumers) can use.
    """

    def method_sub(self, arg: list[str], /) -> list[str]:
        """Return the supplied list unchanged.

        Args:
            arg (list[str]): A list of strings that will be returned
                verbatim.

        Returns:
            list[str]: The same list that was passed in.

        Notes:
            This method does not modify the input list and simply
            forwards it. It exists only to provide a concrete
            implementation for the ``pkg1.main`` module to call.
        """
        return arg
