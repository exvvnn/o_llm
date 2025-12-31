from typing import Callable


def main(_class, function: Callable()):
    instance = _class()
    result = function(instance)
    print(result)


if __name__ == "__main__":
    main(*args, **kwargs)