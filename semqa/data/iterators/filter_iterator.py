from typing import Dict, Union, Iterable, Iterator, List, Optional, Tuple, Deque
from collections import deque
from typing import Iterable, Deque
import logging
import random

from collections import defaultdict

from allennlp.common.util import lazy_groups_of
from allennlp.data.instance import Instance
from allennlp.data.iterators.data_iterator import DataIterator
from allennlp.data.dataset import Batch

import datasets.drop.constants as constants

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


@DataIterator.register("filter")
class DataFilterIterator(DataIterator):
    """
    A very basic iterator that takes a dataset, possibly shuffles it, and creates fixed sized batches.

    It takes the same parameters as :class:`allennlp.data.iterators.DataIterator`
    """

    def __init__(
        self,
        batch_size: int = 32,
        instances_per_epoch: int = None,
        max_instances_in_memory: int = None,
        cache_instances: bool = False,
        track_epoch: bool = False,
        maximum_samples_per_batch: Tuple[str, int] = None,
        filter_key: str = "strongly_supervised",
        supervision_keys: List[str] = ["program_supervised", "qattn_supervised", "execution_supervised"],
        filter_instances: bool = False,
        filter_for_epochs: int = 0,
    ) -> None:
        super(DataFilterIterator, self).__init__(
            batch_size=batch_size,
            instances_per_epoch=instances_per_epoch,
            max_instances_in_memory=max_instances_in_memory,
            cache_instances=cache_instances,
            track_epoch=track_epoch,
            maximum_samples_per_batch=maximum_samples_per_batch,
        )

        self.filter_instances = filter_instances
        # This is the field_name in the instances that contains filter-ing bool
        self.filter_key = filter_key
        self.filter_for_epochs = filter_for_epochs
        self.supervision_keys = supervision_keys

    def _create_batches(self, instances: Iterable[Instance], shuffle: bool) -> Iterable[Batch]:
        # First break the dataset into memory-sized lists:
        for instance_list in self._memory_sized_lists(instances):
            instances_w_epoch_num = 0
            for instance in instances:
                if "epoch_num" in instance.fields:
                    instances_w_epoch_num += 1

            print(f"\nInstances: {len(instance_list)}")

            epochs_list = list(self._epochs.values())
            assert len(epochs_list) == 1, f"Multiple epoch keys: {self._epochs}"
            epoch_num = epochs_list[0]
            if self._track_epoch:
                for instance in instance_list:
                    instance.fields["epoch_num"] = epoch_num

            supervision_dict = defaultdict(int)
            qtype_dict = defaultdict(int)
            for instance in instance_list:
                for key in self.supervision_keys:
                    supervision_dict[key] += 1 if instance[key].metadata else 0
                qtype_dict[instance["qtypes"].metadata] += 1

            print(f"QType: {qtype_dict}")

            # These QType instances will not be kept in the first curriculum even if supervised
            NO_CURRICULUM = [
                constants.COUNT_filter_find_qtype,
                constants.MAX_filter_find_qtype,
                constants.MIN_filter_find_qtype,
                constants.NUM_filter_find_qtype,
            ]

            filtered_instance_list = []
            if self.filter_instances and epoch_num < self.filter_for_epochs:
                for instance in instance_list:
                    if (
                        any(instance[key].metadata is True for key in self.supervision_keys)
                        and not instance["qtypes"].metadata in NO_CURRICULUM
                    ):
                        filtered_instance_list.append(instance)
            else:
                filtered_instance_list = instance_list

            print(f"SupervisionDict: {supervision_dict}")
            print(f"Filtered Instances: {len(filtered_instance_list)}")

            if shuffle:
                random.shuffle(filtered_instance_list)
            iterator = iter(filtered_instance_list)
            excess: Deque[Instance] = deque()
            # Then break each memory-sized list into batches.
            for batch_instances in lazy_groups_of(iterator, self._batch_size):
                for possibly_smaller_batches in self._ensure_batch_is_sufficiently_small(batch_instances, excess):
                    batch = Batch(possibly_smaller_batches)
                    yield batch
            if excess:
                yield Batch(excess)
