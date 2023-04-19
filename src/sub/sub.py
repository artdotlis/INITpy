class MySub:
    """_summary_"""

    def method_sub(self, arg: set[str], /) -> list[str]:
        """_summary_

        Args:
            arg (set[str]): _description_

        Returns:
            list[str]: _description_
        """
        return list(arg)
