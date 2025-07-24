
# Introduction
This simple image viewer is specialized in AI Super Resolution Upscaling in real-time.
Using current Super Resolution AI models for improved perceived upscaling quality. 
It has all the basic image viewing functions and many visual and speed focused implementations.
All the internal image scaling are performed by GPU accelerated shaders.
Current version contains about 500 lines of Python codes plus external shader files.
This project shares its Super Resolution backends with my other repos.
Ths project will run cross-platform under both Windows and Linux (under testing).

# Features
- GPU accelerated AI SRCNN for high quality 2x or 4x zoom.
- GPU accelerated Lanczos or Bicubic fit to screen image browsing.
- Pygame(SDL) based cross-platform GUI, highly consistant and responsive.
- Fast image viewing folder by folder.
- All image decodings are prefetched and cached for speed.
- Auto bookmark and resume for unlimited number of folders.
- PIXIV specific file grouping and batch moving/deleting functions.

# Future plans
- Implement other HLSL/GLSL shaders cross-platform using the compushady library.
- Implement other experimental Super Resolution AI models with simple pytorch calls.

# Acknowledgement and Special Thanks
This project contains codes based on the following projects/libraries:
- https://github.com/Blinue/Magpie
- https://github.com/funnyplanter/CuNNy
- https://github.com/rdeioris/compushady
- https://www.pygame.org/
