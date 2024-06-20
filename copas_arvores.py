# -*- coding: utf-8 -*-
"""
/***************************************************************************
 copasarvores
                                 A QGIS plugin
 teste
                              -------------------
        begin                : 2017-06-16
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Pedro Silva
        email                : up201007485@fc.up.pt
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo, QVariant
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QMessageBox
from qgis.core import edit, QgsRasterBandStats, QgsRasterLayer, QgsVectorLayer
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from copas_arvores_dialog import copasarvoresDialog
import os.path
from processing import Processing, QgsApplication


class copasarvores:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'copasarvores_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = copasarvoresDialog()
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&copas arvores')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'copasarvores')
        self.toolbar.setObjectName(u'copasarvores')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('copasarvores', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.dlg.pushButton.clicked.connect(self.inputfile)
        self.dlg.pushButton_2.clicked.connect(self.inputfile_2)
        self.dlg.pushButton_3.clicked.connect(self.outputfile)
        self.dlg.pushButton_4.clicked.connect(self.outputfile_2)
        icon_path = ':/plugins/copasarvores/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'calculo copas arvores'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def inputfile(self):
        self.dlg.lineEdit.setText(QFileDialog.getOpenFileName())

    def inputfile_2(self):
        self.dlg.lineEdit_2.setText(QFileDialog.getOpenFileName())

    def outputfile(self):
        self.dlg.lineEdit_3.setText(QFileDialog.getSaveFileName())

    def outputfile_2(self):
        self.dlg.lineEdit_4.setText(QFileDialog.getSaveFileName())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&copas arvores'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            inputLayer = self.dlg.lineEdit.text() # imagem multiespectral
            inputLayer2 = self.dlg.lineEdit_2.text() # imagem ndvi
            multiEspectral = QgsRasterLayer(str(inputLayer),"multiespectral")

            totalBandas = multiEspectral.bandCount() # numero total de bandas
            xPixel = multiEspectral.width()
            yPixel = multiEspectral.height()
            totalPixel = xPixel*yPixel
            minx = multiEspectral.extent().xMinimum()
            maxx = multiEspectral.extent().xMaximum()
            miny = multiEspectral.extent().yMinimum()
            maxy = multiEspectral.extent().yMaximum()
            extentRaster = str(minx) + ',' + str(maxx) + ',' + str(miny) + ',' + str(maxy) 

            Processing.initialize()
            
            # Separar a imagem em bandas, armazenando numa lista em compressão
            split = os.path.join(QFileInfo(QgsApplication.qgisUserDbFilePath()).path(), 'split.tif')
            Processing.runAlgorithm("otb:splitimage", None, inputLayer, 512, split)
            bandas=[os.path.join(QFileInfo(QgsApplication.qgisUserDbFilePath()).path(), 'split_'+str(nband)+'.tif') for nband in range(totalBandas)]
            
            
            # Segmentação
            minsize = 100
            seed = os.path.join(QFileInfo(QgsApplication.qgisUserDbFilePath()).path(), 'semente.tif')
            # Imagem inicial com pontos semente
            Processing.runAlgorithm("grass7:i.segment", None, bandas, 0.05, 0, 0, minsize, 512, 20, None, None, False, False, str(extentRaster), 0, seed, None)
            
            # Segmentação através das imagens 
            segmentada = os.path.join(QFileInfo(QgsApplication.qgisUserDbFilePath()).path(), 'segmentada.tif')
            for thresh in [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65]: 
                Processing.runAlgorithm("grass7:i.segment", None, bandas, thresh, 0, 0, minsize, 512, 20, seed, None, False, False, str(extentRaster), 0, segmentada, None)
                seed = segmentada
            
            # Classificação não supervisonada
            trainingSet = int(totalPixel*0.00705) 
            classificada = os.path.join(QFileInfo(QgsApplication.qgisUserDbFilePath()).path(), 'classificada.tif')
            Processing.runAlgorithm("otb:unsupervisedkmeansimageclassification", None, inputLayer2, 1024, segmentada, trainingSet, 5, 1000, 0.0001, classificada, None)
            
            # Valor máximo da imagem classificada
            class_rc = QgsRasterLayer(classificada, 'class_rc')
            max_rc = class_rc.dataProvider().bandStatistics(1, QgsRasterBandStats.All, class_rc.extent()).maximumValue 
           
            
            # Identificação das copas das árvores como valor 1 e os restantes elementos com valor 0
            extraida = os.path.join(QFileInfo(QgsApplication.qgisUserDbFilePath()).path(), 'extraida.tif')
            Processing.runAlgorithm("gdalogr:rastercalculator", None, class_rc, 1, None, None, None, None, None, None, None, None, None, None, "A==" + str(max_rc), 0, 4, None, extraida) 
            
            # Conversão da imagem classificada em ficheiro vectorial
            copas = self.dlg.lineEdit_3.text() + '.shp' # output shapefile
            Processing.runAlgorithm("gdalogr:polygonize", None, extraida, 'DN', copas)

            layer = QgsVectorLayer(copas,"layer","ogr")
            
            # Excluir objetos da shapefile, através do valor da área, atributo e rácio da bounding box
            dif_racio=0.55

            with edit(layer):
                for f in layer.getFeatures():
                    area = f.geometry().area()
                    height = f.geometry().boundingBox().height()
                    width = f.geometry().boundingBox().width()
                    racio = height/width
                    if area<=1 or area>=50 or f['DN']!=1 or racio<1-dif_racio or racio>1+dif_racio:
                        layer.deleteFeature(f.id())
            
            # Tabela com as métricas das copas
            info = self.dlg.lineEdit_4.text() + '.txt'
            tabela = open(info, 'w') # output ficheiro de texto
            header = '%s %s %s %s %s\n' % ('ID', 'Área', 'Perímetro', 'x(centroide)', 'y(centroide)') # cabeçalho
            tabela.write(header)

            totalArvores = 0 # Contar número de árvores
            totalArea = 0 # somar as áreas das copas
             
            for f in layer.getFeatures():
                area = f.geometry().area() # area
                perimetro = f.geometry().length() # perimetro
                centroid_x = f.geometry().boundingBox().center().x() # coordenada x do centroide
                centroid_y = f.geometry().boundingBox().center().y() # coordenada y do centroide
                line = '%i %f %f %f %f\n' % (f.id(), area, perimetro, centroid_x, centroid_y) # linha com as métricas para cada copsa de arvore
                unicode_line = line.encode('utf-8')
                tabela.write(unicode_line)
                totalArea += area
                totalArvores += 1

            line_1 = '\n-----------------------------------------############------------------------------------------\n'
            tabela.write(line_1)

            line_2 = '\nNúmero de árvores total = ' + str(totalArvores) + '\n'
            tabela.write(line_2)

            line_3 = 'Área total de árvores = ' + str(totalArea) + '\n'
            tabela.write(line_3)

            tabela.close()