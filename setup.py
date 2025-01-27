import cx_Freeze
from cx_Freeze import setup, Executable  

# Define the application's metadata
executables = [Executable(
    script="notasnakev2.1 1366x768.py", 
    base="Win32GUI", 
    icon="naslogo.ico" 
)]


build_options = {
    "packages": ["pygame"],
}


setup(
    name="NotASnake v2.1",
    version="2.1",
    description="NotASnake - Free Community-builded snake game. /// We are SKD ///",
    executables=executables,
    options={"build_exe": build_options},
)

