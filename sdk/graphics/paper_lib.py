import time

from PIL import Image, ImageDraw

from sdk.graphics import PaperDynamic, page_lib


class PaperTheme(PaperDynamic):
    def __init__(self, env, background_image=Image.new("RGB", (296, 128), (255, 255, 255))):
        super().__init__(env, background_image)
        self.dock_image = Image.open(open("resources/images/docker.jpg", "rb"))
        self.__docker_active = False
        self.inited = False
        self.pages["appList"] = page_lib.ApplistPage(self, "appList")
        self.suspended_touchpad = None

    def appbox_click_handler(self):
        if self.__docker_active:
            self.suspended_touchpad = None
            self.__docker_active = False
            self.change_page("appList", to_stack=True)
            self.pages["appList"].show()

    def settings_click_handler(self):
        if self.__docker_active:
            self.suspended_touchpad = None
            self.__docker_active = False
            self.env.open_app("系统选项")

    def close_docker(self):
        if self.__docker_active:
            if self.suspended_touchpad:
                self.env.touch_handler.recover(self.suspended_touchpad)
                self.suspended_touchpad = None
            self.__docker_active = False
            self.update_anyway()

    def docker_clicked_handler(self):
        if (self.nowPage != "mainPage") or self.__docker_active or (not self.inited):
            return
        self.suspended_touchpad = self.env.touch_handler.suspend()
        self.env.touch_handler.add_clicked(
            (60, 100, 0, 30), self.appbox_click_handler)
        self.env.touch_handler.add_clicked(
            (195, 235, 0, 30), self.settings_click_handler)
        self.env.touch_handler.add_clicked(
            (0, 296, 30, 128), self.close_docker)
        self.__docker_active = True
        self.update_anyway()
        for i in range(5):
            time.sleep(1)
            if not self.__docker_active:
                return
        self.__docker_active = False
        if self.suspended_touchpad:
            self.env.touch_handler.recover(self.suspended_touchpad)
            self.suspended_touchpad = None
        self.update_anyway()

    def init(self):
        super().init()
        self.env.touch_handler.add_clicked(
            (0, 296, 0, 30), self.docker_clicked_handler)

    def recover(self):
        super().recover()
        if self.nowPage == "mainPage":
            self.env.touch_handler.add_clicked(
                (0, 296, 0, 30), self.docker_clicked_handler)

    def build(self) -> Image:
        new_image = super().build()
        if self.__docker_active:
            new_image.paste(self.dock_image, (60, 0))
        self.image_old = new_image  # TODO:删除image_old
        return new_image

    def change_page(self, name, refresh=None, to_stack=False):
        super().change_page(name, refresh, to_stack)
        if name == "mainPage":
            self.env.touch_handler.add_clicked(
                (0, 296, 0, 30), self.docker_clicked_handler)


class PaperApp(PaperDynamic):
    def __init__(self, env, app_name, icon=None, background_image=Image.new("RGBA", (296, 128), (255, 255, 255, 255))):
        super().__init__(env, background_image=background_image)
        self.first_init = True
        self.__bar_active = False
        self.bar_image = Image.open(open("resources/images/app_control.jpg", "rb"))
        self.more_event = None
        self.more_list = None
        self.args = []
        self.kwargs = {}
        self.suspended_touched = None
        self.name = app_name
        self.clock_font = self.env.fonts.get_heiti(18)
        self.title_font = self.env.fonts.get_heiti(19)
        self.more_cover = Image.new("RGB", (10, 20), "white")
        self.title = self.name
        if icon:
            self.icon = icon
        else:
            self.icon = self.env.Images.none20px

    def close_click_handler(self, long):
        if self.__bar_active:
            if long >= 1:
                self.env.back_home(True)
            else:
                self.env.back_home()
            self.__bar_active = False

    def more_click_handler(self):
        if self.__bar_active:
            self.__bar_active = False
            if self.more_event:
                self.more_event(*self.args, **self.kwargs)

    def close_bar(self):
        if self.__bar_active:
            self.__bar_active = False
            if self.suspended_touched:
                self.env.touch_handler.recover(self.suspended_touched)
                self.suspended_touched = None
            self.update_anyway()

    def bar_clicked_handler(self):
        if self.__bar_active or (not self.inited):
            return
        self.suspended_touched = self.env.touch_handler.suspend()
        self.env.touch_handler.add_clicked(
            (0, 296, 30, 128), self.close_bar)
        self.env.touch_handler.add_clicked_with_time(
            (266, 296, 0, 30), self.close_click_handler)
        self.env.touch_handler.add_clicked(
            (236, 266, 0, 30), self.more_click_handler
        )
        self.__bar_active = True
        self.update_anyway()
        for _ in range(5):
            time.sleep(1)
            if not self.__bar_active:
                return
        self.__bar_active = False
        if self.suspended_touched:
            self.env.touch_handler.recover(self.suspended_touched)
            self.suspended_touched = None
        self.update_anyway()

    def init(self):
        if self.first_init:
            self.first_init = False
        self.env.touch_handler.add_clicked(
            (266, 296, 0, 30), self.bar_clicked_handler)
        super().init()

    def recover(self):
        super().recover()
        self.env.touch_handler.add_clicked(
            (266, 296, 0, 30), self.bar_clicked_handler)

    def set_more_func(self, func, *args, **kwargs):  # todo: 改写more list
        self.more_event = func
        self.args = args
        self.kwargs = kwargs

    def build(self) -> Image:
        new_image = super().build()
        if self.__bar_active:
            new_image.paste(self.bar_image, (0, 0))
            if not self.more_event:
                new_image.paste(self.more_cover, (246, 3))
            new_image.paste(self.icon, (3, 3))
            image_draw = ImageDraw.ImageDraw(new_image)
            image_draw.text((30, 4), self.title, fill="black", font=self.title_font)
            image_draw.text((150, 7), time.strftime("%H : %M", time.localtime()), fill="black", font=self.clock_font)
        return new_image

    def change_page(self, name, refresh=None, to_stack=False):
        super().change_page(name, refresh, to_stack)
        self.env.touch_handler.add_clicked(
            (266, 296, 0, 30), self.bar_clicked_handler)
