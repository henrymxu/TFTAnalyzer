import multiprocessing

from tft import parser, board, utils

ShopTask = "shop"
HealthbarsTask = "healthbars"
FinishTask = "finish"


class Handler:
    def __init__(self, result_queue):
        ctx = multiprocessing.get_context('spawn')
        self.__processes = []
        self.__task_queue = ctx.Queue()

        for _ in range(multiprocessing.cpu_count() - 1):
            process = ctx.Process(target=TaskHandler, args=(self.__task_queue, result_queue))
            self.__processes.append(process)

    def start(self):
        for process in self.__processes:
            process.start()

    def finish(self):
        time = utils.start_timer()
        for _ in range(multiprocessing.cpu_count() - 1):
            self.queue_finish_task()
        for process in self.__processes:
            process.join()
        print("Backlogged {} seconds".format(utils.end_timer(time)))

    def queue_finish_task(self):
        self._queue_task(FinishTask, None, None, None)

    def queue_shop_task(self, img, gameBoard, stage):
        functions = [parser.parse_level, parser.parse_gold, parser.parse_shop]
        imgs = [board.crop_level(img, gameBoard), board.crop_gold(img, gameBoard), board.crop_shop(img, gameBoard)]
        self._queue_task(ShopTask, imgs, functions, stage)

    def queue_healthbars_task(self, img, gameBoard, stage):
        functions = [parser.parse_healthbars]
        imgs = [board.crop_healthbar(img, gameBoard, 0), board.crop_healthbar(img, gameBoard, 1)]
        self._queue_task(HealthbarsTask, imgs, functions, stage)

    def _queue_task(self, mode, imgs, functions, stage):
        self.__task_queue.put(_serialize_task(mode, imgs, functions, stage))


def TaskHandler(task_queue, results_queue):
    while True:
        task = task_queue.get()
        mode, imgs, functions, stage = _deserialize_task(task)
        if mode == FinishTask:
            break
        if mode == ShopTask:
            contents = _handle_shop(stage, imgs, functions)
        else:  # mode == "healthbars
            contents = _handle_healthbars(stage, imgs, functions)
        results_queue.put({"mode": mode, "contents": contents})


def _serialize_task(mode, imgs, functions, stage):
    return mode, imgs, functions, stage


def _deserialize_task(task):
    return task[0], task[1], task[2], task[3]


def _handle_shop(stage, imgs, functions):
    assert (len(imgs) == 3)
    assert (len(functions) == 3)
    level = functions[0](imgs[0])
    gold = functions[1](imgs[1])
    shop = functions[2](imgs[2])
    return {"stage": stage, "units": shop, "level": level, "gold": gold}


def _handle_healthbars(stage, imgs, functions):
    assert (len(imgs) == 2)
    assert (len(functions) == 1)
    healthbars = functions[0](imgs[0], imgs[1])
    return {"stage": stage, "healthbars": healthbars}
