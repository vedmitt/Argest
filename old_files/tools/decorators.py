import functools
import time
import traceback


class RunTimer:
    def __init__(self, out):
        self.out = out

    def timer(self, func):
        """Print the runtime of the decorated function"""

        @functools.wraps(func)
        def wrapper_timer(*args, **kwargs):
            start_time = time.perf_counter()  # 1
            value = func(*args, **kwargs)
            end_time = time.perf_counter()  # 2
            run_time = end_time - start_time  # 3
            self.out.print(f"\nОперация завершена за {run_time:.4f}сек.")
            # print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
            return value

        return wrapper_timer

# def exception_handler(func, out=None, err_text=f'Упсс... Что-то пошло не так :(', exceptions=Exception):  # --> tuple
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except exceptions:
#             full_traceback = traceback.format_exc()
#             if out is not None:
#                 tabWidget = out.tabWidget
#                 tabWidget.setCurrentIndex(tabWidget.count()-1)
#                 out.print(1, -1, err_text)
#                 out.print(1, 0, full_traceback)
#             else:
#                 print(full_traceback)
#     return wrapper

# class ExceptionHandle:  # working
#     def __init__(self, output_tool):
#         self.out = output_tool
#
#     def exception_handler(self, func, err_text=f'Упсс... Что-то пошло не так :(', exceptions=Exception):  # --> tuple
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             try:
#                 return func(*args, **kwargs)
#             except exceptions:
#                 full_traceback = traceback.format_exc()
#                 if self.out is not None:
#                     self.tabWidget = self.out.tabWidget
#                     self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)
#                     self.out.print(1, -1, err_text)
#                     self.out.print(1, 0, full_traceback)
#                 else:
#                     print(full_traceback)
#         return wrapper


class ExceptionHandle:
    def __init__(self, function, output_tool=None, err_text=f'Упсс... Что-то пошло не так :(', exceptions=Exception):
        self.function = function
        self.out = output_tool
        self.err_text = err_text
        self.exceptions = exceptions

    def __call__(self, *args, **kwargs):
        try:
            return self.function(*args, **kwargs)
        except self.exceptions:
            full_traceback = traceback.format_exc()
            if self.out is not None:
                # self.out.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)
                self.out.print(self.err_text, -1)
                self.out.print(full_traceback)
            else:
                print(full_traceback)
