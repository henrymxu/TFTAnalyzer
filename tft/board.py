from tft import utils, image_utils


class Board:
    def __init__(self, size):
        self.__vertices, self.__scaling = _generate_board_data(size)

    def getScaling(self):
        return self.__scaling

    def getGold(self):
        return self.__vertices["gold"]

    def getShop(self):
        return self.__vertices["shop"]

    def getLevel(self):
        return self.__vertices["level"]

    def getStage(self):
        return self.__vertices["stage"]

    def getStageEarly(self):
        return self.__vertices["stage_early"]

    def getTimer(self):
        return self.__vertices["timer"]

    def getTimerEarly(self):
        return self.__vertices["timer_early"]

    def getPlayers(self):
        return self.__vertices["players"]

    def getHealthBarCircles(self):
        return self.__vertices["health_bar_circles"]

    def getHealthBars1(self):
        return self.__vertices["health_bar_names_1"], self.__vertices["health_bar_values_1"]

    def getHealthBars2(self):
        return self.__vertices["health_bar_names_2"], self.__vertices["health_bar_values_2"]

    def getHealthBars(self, circles):
        return _find_healthbars_from_circles(circles, self.__vertices["health_bar_circles_size_info"])


def _get_screen_size_data(size):
    data = utils.open_json_file("data/screen_sizes.json")
    user_resolution = size[1]
    range = 0.1
    for resolution in data:
        value = int(resolution)
        min_res = value * (1 - range)
        max_res = value * (1 + range)
        if min_res < user_resolution < max_res:
            return data[resolution]
    utils.exit_with_error("Unsupported screen size: {}".format(size[1]))


def _generate_board_data(size):
    size_data = _get_screen_size_data(size)
    vertices_data = size_data["contents"]
    vertices = {"gold": __create_rectangle_from_data(vertices_data["gold"]),
                "shop": __create_row_of_rectangles_from_data(vertices_data["shop"], 5),
                "level": __create_rectangle_from_data(vertices_data["level"]),
                "stage": __create_rectangle_from_data(vertices_data["stage"]),
                "stage_early": __create_rectangle_from_data(vertices_data["stage_early"]),
                "timer": __create_rectangle_from_data(vertices_data["timer"]),
                "timer_early": __create_rectangle_from_data(vertices_data["timer_early"]),
                "health_bar_names_1": __create_column_of_rectangles_from_data(
                    vertices_data["health_bar_names_top_to_bottom"], 8),
                "health_bar_values_1": __create_column_of_rectangles_from_data(
                    vertices_data["health_bar_values_top_to_bottom"], 8),
                "health_bar_names_2": __create_column_of_rectangles_from_data(
                    vertices_data["health_bar_names_bottom_to_top"], 8),
                "health_bar_values_2": __create_column_of_rectangles_from_data(
                    vertices_data["health_bar_values_bottom_to_top"], 8),
                "players": __create_grid_of_rectangles_from_data(vertices_data["players"], 2, 4),
                "health_bar_circles": __create_column_of_rectangles_from_data(vertices_data["health_bar_circles"], 8),
                "health_bar_circles_size_info": vertices_data["health_bar_circles"]}
    scaling = size_data["scaling"]
    return vertices, scaling


def __create_grid_of_rectangles_from_data(data, rows, columns):
    return __create_grid_of_rectangles(data["x"], data["y"], data["width"], data["height"], data["x_gap"],
                                       data["y_gap"], rows, columns)


def __create_column_of_rectangles_from_data(data, rows):
    return __create_column_of_rectangles(data["x"], data["y"], data["width"], data["height"], data["gap"], rows)


def __create_row_of_rectangles_from_data(data, columns):
    return __create_row_of_rectangles(data["x"], data["y"], data["width"], data["height"], data["gap"], columns)


def __create_rectangle_from_data(data):
    return __create_rectangle(data["x"], data["y"], data["width"], data["height"])


def __create_grid_of_rectangles(x_offset, y_offset, width, height, x_gap, y_gap, rows, columns):
    result = []
    for row in range(0, rows):
        for column in range(0, columns):
            ys = [0, height]
            ys = [y + (y_offset + row * (height + y_gap)) for y in ys]
            xs = [0, width]
            xs = [x + (x_offset + column * (width + x_gap)) for x in xs]
            # leftTop, rightTop, rightBottom, leftBottom
            vertices = [[xs[0], ys[0]], [xs[1], ys[0]], [xs[1], ys[1]], [xs[0], ys[1]]]
            result.append(vertices)
    return result


def __create_column_of_rectangles(x_offset, y_offset, width, height, gap, rows):
    result = []
    for row in range(0, rows):
        ys = [0, height]
        ys = [y + (y_offset + row * (height + gap)) for y in ys]
        xs = [0, width]
        xs = [x + x_offset for x in xs]
        # leftTop, rightTop, rightBottom, leftBottom
        vertices = [[xs[0], ys[0]], [xs[1], ys[0]], [xs[1], ys[1]], [xs[0], ys[1]]]
        result.append(vertices)
    return result


def __create_row_of_rectangles(x_offset, y_offset, width, height, gap, columns):
    result = []
    for column in range(0, columns):
        ys = [0, height]
        ys = [y + y_offset for y in ys]
        xs = [0, width]
        xs = [x + (x_offset + column * (width + gap)) for x in xs]
        # leftTop, rightTop, rightBottom, leftBottom
        vertices = [[xs[0], ys[0]], [xs[1], ys[0]], [xs[1], ys[1]], [xs[0], ys[1]]]
        result.append(vertices)
    return result


def __create_rectangle(x_offset, y_offset, width, height):
    y = [y_offset, y_offset + height]
    x = [x_offset, x_offset + width]
    vertices = [[x[0], y[0]], [x[1], y[0]], [x[1], y[1]], [x[0], y[1]]]
    return [vertices]


def _find_healthbars_from_circles(circles, size_data):
    v_results = []
    n_results = []
    own_circle_radius_thresh = size_data["own_circle_radius"]
    buffer_spacing = size_data["buffer_spacing"]
    y_offset = size_data["y"]
    for circle in circles:
        x_circle, y_circle, r = int(circle[0] / 2), int(circle[1] / 2), int(circle[2] / 2)
        n_x, n_height, n_width = size_data["name_x"], size_data["name_height"], size_data["name_width"]
        n_y = y_offset + y_circle - int(n_height / 2) - int(buffer_spacing / 2)
        n_results.append(__create_rectangle(n_x, n_y, n_width, n_height + buffer_spacing * 2)[0])

        v_x, v_height, v_width = size_data["value_x"], size_data["value_height"], size_data["value_width"]
        if r > own_circle_radius_thresh:
            n_results[-1] = None
            v_x, v_height, v_width = size_data["own_value_x"], size_data["own_value_height"], size_data[
                "own_value_width"]
        v_y = y_offset + y_circle - int(v_height / 2) - int(buffer_spacing / 2)

        v_results.append(__create_rectangle(v_x, v_y, v_width, v_height + buffer_spacing * 2)[0])
        y_offset += (size_data["height"] + size_data["gap"])
    return n_results, v_results


def crop_stage(img, gameBoard):
    return image_utils.crop_shape(img, gameBoard.getStage()[0], 200)


def crop_stage_early(img, gameBoard):
    return image_utils.crop_shape(img, gameBoard.getStageEarly()[0], 200)


def crop_timer(img, gameBoard):
    return image_utils.crop_shape(img, gameBoard.getTimer()[0], 200)


def crop_timer_early(img, gameBoard):
    return image_utils.crop_shape(img, gameBoard.getTimerEarly()[0], 200)


def crop_header(img, gameBoard):
    return crop_stage(img, gameBoard), crop_timer(img, gameBoard)


def crop_header_early(img, gameBoard):
    return crop_stage_early(img, gameBoard), crop_timer_early(img, gameBoard)


def crop_level(img, gameBoard):
    return image_utils.crop_shape(img, gameBoard.getLevel()[0], 300)


def crop_gold(img, gameBoard):
    return image_utils.crop_shape(img, gameBoard.getGold()[0], 150)


def crop_shop(img, gameBoard):
    return image_utils.crop_shapes(img, gameBoard.getShop(), 200)


def crop_healthbars_legacy(img, gameBoard, direction):
    if direction == 0:
        names = image_utils.crop_shapes(img, gameBoard.getHealthBars1()[0], 150)
        values = image_utils.crop_shapes(img, gameBoard.getHealthBars1()[1], 150)
    else:
        names = image_utils.crop_shapes(img, gameBoard.getHealthBars2()[0], 150)
        values = image_utils.crop_shapes(img, gameBoard.getHealthBars2()[1], 150)
    return names, values


def crop_players(img, gameBoard):
    return image_utils.crop_shapes(img, gameBoard.getPlayers(), 200)


def crop_healthbar_circles(img, gameBoard):
    return image_utils.crop_shapes(img, gameBoard.getHealthBarCircles(), 200)


def crop_healthbars(img, gameBoard, circles):
    name_shapes, value_shapes = gameBoard.getHealthBars(circles)
    names = image_utils.crop_shapes(img, name_shapes, gameBoard.getScaling()["healthbar_name"])
    values = image_utils.crop_shapes(img, value_shapes, gameBoard.getScaling()["healthbar_value"])
    return names, values
