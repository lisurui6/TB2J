"""
This file is copied from the p_tqdm package. It is copied because the pip version, which is not compatible with python3.10, is not update to date as of the day of 30th, April, 2022. Once it is updated, we'll switch back to the p_tqdm library on pip. 

Below is the original licence:
==================================================
Copyright (c) 2020 Kyle Swanson                                                       

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
"""Map functions with tqdm progress bars for parallel and sequential processing.

p_map: Performs a parallel ordered map.
p_imap: Returns an iterator for a parallel ordered map.
p_umap: Performs a parallel unordered map.
p_uimap: Returns an iterator for a parallel unordered map.
t_map: Performs a sequential map.
t_imap: Returns an iterator for a sequential map.
"""

from collections.abc import Sized
from typing import Any, Callable, Generator, Iterable, List

from pathos.helpers import cpu_count
from pathos.multiprocessing import ProcessPool as Pool
from tqdm.auto import tqdm


def _parallel(ordered: bool, function: Callable, *iterables: Iterable,
              **kwargs: Any) -> Generator:
    """Returns a generator for a parallel map with a progress bar.

    Arguments:
        ordered(bool): True for an ordered map, false for an unordered map.
        function(Callable): The function to apply to each element of the given Iterables.
        iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.

    Returns:
        A generator which will apply the function to each element of the given Iterables
        in parallel in order with a progress bar.
    """

    # Extract num_cpus
    num_cpus = kwargs.pop('num_cpus', None)

    # Determine num_cpus
    if num_cpus is None:
        num_cpus = cpu_count()
    elif type(num_cpus) == float:
        num_cpus = int(round(num_cpus * cpu_count()))

    # Determine length of tqdm (equal to length of shortest iterable or total kwarg), if possible
    total = kwargs.pop('total', None)
    lengths = [
        len(iterable) for iterable in iterables if isinstance(iterable, Sized)
    ]
    length = total or (min(lengths) if lengths else None)

    # Create parallel generator
    map_type = 'imap' if ordered else 'uimap'
    pool = Pool(num_cpus)
    map_func = getattr(pool, map_type)

    for item in tqdm(map_func(function, *iterables), total=length, **kwargs):
        yield item

    pool.clear()


def p_map(function: Callable, *iterables: Iterable,
          **kwargs: Any) -> List[Any]:
    """Performs a parallel ordered map with a progress bar."""

    ordered = True
    generator = _parallel(ordered, function, *iterables, **kwargs)
    result = list(generator)

    return result


def p_imap(function: Callable, *iterables: Iterable,
           **kwargs: Any) -> Generator:
    """Returns a generator for a parallel ordered map with a progress bar."""

    ordered = True
    generator = _parallel(ordered, function, *iterables, **kwargs)

    return generator


def p_umap(function: Callable, *iterables: Iterable,
           **kwargs: Any) -> List[Any]:
    """Performs a parallel unordered map with a progress bar."""

    ordered = False
    generator = _parallel(ordered, function, *iterables, **kwargs)
    result = list(generator)

    return result


def p_uimap(function: Callable, *iterables: Iterable,
            **kwargs: Any) -> Generator:
    """Returns a generator for a parallel unordered map with a progress bar."""

    ordered = False
    generator = _parallel(ordered, function, *iterables, **kwargs)

    return generator


def _sequential(function: Callable, *iterables: Iterable,
                **kwargs: Any) -> Generator:
    """Returns a generator for a sequential map with a progress bar.

    Arguments:
        function(Callable): The function to apply to each element of the given Iterables.
        iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.

    Returns:
        A generator which will apply the function to each element of the given Iterables
        sequentially in order with a progress bar.
    """

    # Determine length of tqdm (equal to length of shortest iterable)
    length = min(
        len(iterable) for iterable in iterables if isinstance(iterable, Sized))

    # Create sequential generator
    for item in tqdm(map(function, *iterables), total=length, **kwargs):
        yield item


def t_map(function: Callable, *iterables: Iterable,
          **kwargs: Any) -> List[Any]:
    """Performs a sequential map with a progress bar."""

    generator = _sequential(function, *iterables, **kwargs)
    result = list(generator)

    return result


def t_imap(function: Callable, *iterables: Iterable,
           **kwargs: Any) -> Generator:
    """Returns a generator for a sequential map with a progress bar."""

    generator = _sequential(function, *iterables, **kwargs)

    return generator
