# Falls back to config.example.h when include/config.h is missing (CI, first build).
# Done here because __has_include also matches the framework's own config.h.
import os

Import("env")

if not os.path.isfile(os.path.join(env.subst("$PROJECT_INCLUDE_DIR"), "config.h")):
    env.Append(CPPDEFINES=["USE_EXAMPLE_CONFIG"])
