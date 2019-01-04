vsvis
==================
**Author**: Vladimir Shteyn 

**GitHub**: [GitHub](https://github.com/mistervladimir)

**LinkedIn**: [LinkedIn](https://www.linkedin.com/in/vladimir-shteyn/)


Introduction
------------------
This is a GUI for visualizing the results of [endocytosis](https://github.com/MisterVladimir/endocytosis), which predicts the centroid of diffraction-limited spots in fluorescence microscopy image data. (For those not familiar with fluorescence microscopy, these images look a lot like those of a night sky filled with stars, in which case each star is a "diffraction-limited spot"). Users may load image and (X, Y) [coördinate](https://www.newyorker.com/culture/culture-desk/the-curse-of-the-diaeresis) data, the latter of which belongs to one of two categories, *ground truth* or *predicted*. Coördinates are represented as small shapes, e.g. circles or diamonds, at their respective (X, Y) locations in the image, and their visual appearance may be customized to the users preference (see below).

Here is the typical workflow. Upon running main.py, the Main Window pops up. It looks like this:
![startup_main_window](https://github.com/MisterVladimir/vsvis/blob/master/docs/images/VS_20190103%20-%20vsvis_screenshot_01_startup_numbered.png)
(1) Image zoom buttons.  
(2) ImageViewer  
(3) Coördinate TableView  
(4) Marker Appearance Editor  
(5) Progress Bar  
(6) Probability Slider

**TO BE CONTINUED**


Installation
------------------
Only installation from source is available right now.


Test
------------------
python setup.py test


Requirements
------------------
pyqt  
qtpy  
pandas  
numpy  
anytree  
vladutils  


License
------------------
This project is licensed under the GNUv3 License - see the
[LICENSE.rst](LICENSE.rst) file for details.
