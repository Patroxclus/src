import maya.cmds as mc
from PySide2.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QVBoxLayout, QWidget, QAbstractItemView

class AnimClip:
    def __init__(self):
        self.frameStart = mc.playbackOptions(q = True, min = True)
        self.frameEnd = mc.playbackOptions(q = True, max = True)
        self.subfix = ""
        self.shouldExport = True

class MayaToUE:
    def __init__(self):
        self.rootJnt = ""
        self.meshes = set()
        self.fileName = ""
        self.animations = []
        self.saveDir = ""

    def SetSelectedAsRootJnt(self):
        selection = mc.ls(sl = True, type = "joint")
        if not selection:
            return False, "No Joint Selected" 

        self.rootJnt = selection[0]
        return True, ""

    def TryAddUnrealRootJnt(self):
        if (not self.rootJnt) or (not mc.objExists(self.rootJnt)):
            return False, "Need to Assign Root Joint First"
        
        # q means query, t means translate, ws means world space.
        currentRootPos = mc.xform(self.rootJnt, q=True, t=True, ws=True)
        if currentRootPos[0] == 0 and currentRootPos[1] == 0 and currentRootPos[2] == 0:
            return False, "Root Joint Already Exists"
        
        rootJntName = self.rootJnt + "_root"
        mc.select(cl=True) # cl meand cancel.
        mc.joint(name = rootJntName)
        mc.parent(self.rootJnt, rootJntName)
        self.rootJnt = rootJntName
        return True, ""

    def SetSelectedAsMeshes(self):
        selection = mc.ls(sl=True)
        if not selection:
            return False, "No Mesh Selected"
        
        meshes = set() # creates a local variable of the type set
        for sel in selection: # loop through everything we select
            shapes = mc.listRelatives(sel, s=True) # find their shape nodes
            if not shapes:
                continue
            for s in shapes: # for each shape node we find
                if mc.objectType(s) == "mesh": #check if there are mesh shapes.
                    meshes.add(sel) # if they are mesh shapes, we will collect them

        if len(meshes) == 0:
            return False, "No Mesh Selected"
        
        self.meshes = meshes
        return True, ""
        
class AnimEntry(QWidget):
    def __init__(self, animClip: AnimClip):
        super().__init__()
        self.animClip = animClip
        self.masterLayout = QHBoxLayout()
        self.setLayout(self.masterLayout)

        self.toggleBox = QCheckBox()
        self.toggleBox.setChecked(animClip.shouldExport)
        self.toggleBox.toggled.connect(self.ToggleBoxToggled)
        self.masterLayout.addWidget(self.toggleBox)

        subfixLabel = QLabel("Subfix: ")
        self.masterLayout.addWidget(subfixLabel)
        self.subfixLineEdit = QLineEdit()
        self.subfixLineEdit.textChanged.connect(self.SubfixTextChanged)
        self.subfixLineEdit.setText(animClip.subfix)
        self.masterLayout.addWidget(self.subfixLineEdit)

        startFrameLabel = QLabel("Start: ")
        self.masterLayout.addWidget(startFrameLabel)
        self.startFrameLineEdit = QLineEdit()
        self.startFrameLineEdit.textChanged.connect(self.StartFrameChanged)
        self.startFrameLineEdit.setText(str(animClip.frameStart))
        self.masterLayout.addWidget(self.startFrameLineEdit)

        endFrameLabel = QLabel("End: ")
        self.masterLayout.addWidget(endFrameLabel)
        self.endFrameLineEdit = QLineEdit()
        self.endFrameLineEdit.textChanged.connect(self.EndFrameChanged)
        self.endFrameLineEdit.setText(str(animClip.frameEnd))
        self.masterLayout.addWidget(self.endFrameLineEdit)

        setRangeBtn = QPushButton("[ - ]")
        setRangeBtn.clicked.connect(self.SetRangeBtnClicked)
        self.masterLayout.addWidget(setRangeBtn)

        removeBtn = QPushButton("[X]")
        removeBtn.clicked.connect(self.RemoveBtnClicked)
        self.masterLayout.addWidget(removeBtn)
    
    def EndFrameChanged(self):
        pass

    def StartFrameChanged(self):
        pass
    
    def SubfixTextChanged(self):
        pass 

    def ToggleBoxToggled(self):
        self.animClip.shouldExport = not self.animClip.shouldExport

    def RemoveBtnClicked(self):
        self.startFrameLineEdit.clear()
        self.endFrameLineEdit.clear()
    
    def SetRangeBtnClicked(self):
        start_frame = mc.playbackOptions(query=True, minTime=True)
        end_frame = mc.playbackOptions(query=True, maxTime=True)
        self.startFrameLineEdit.setText(str(start_frame))
        self.endFrameLineEdit.setText(str(end_frame))

class MayaToUEWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.mayaToUE = MayaToUE()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.jointLineEdit = QLineEdit()
        self.jointLineEdit.setEnabled(False) # make it grayed out.
        self.masterLayout.addWidget(self.jointLineEdit)

        setSelectedAsRootJntBtn = QPushButton("Set Selected As Root Joint")
        setSelectedAsRootJntBtn.clicked.connect(self.SetSelectedAsRootBtnClicked)
        self.masterLayout.addWidget(setSelectedAsRootJntBtn)

        addUnrealRootBtn = QPushButton("Add Unreal Root Joint")
        addUnrealRootBtn.clicked.connect(self.AddUnrealRootBtnClicked)
        self.masterLayout.addWidget(addUnrealRootBtn)

        self.meshList = QListWidget()
        self.meshList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.meshList.itemSelectionChanged.connect(self.MeshListSelectionChanged)
        self.masterLayout.addWidget(self.meshList)
        assignSelectedMeshBtn = QPushButton("Assign Selected Meshs")
        assignSelectedMeshBtn.clicked.connect(self.AssignSelectedMeshBtnClicked)
        self.masterLayout.addWidget(assignSelectedMeshBtn) 
        testAnimEntry = AnimEntry(AnimClip())
        self.masterLayout.addWidget(testAnimEntry)

    def AssignSelectedMeshBtnClicked(self):
        success, msg = self.mayaToUE.SetSelectedAsMeshes()
        if success:
            self.meshList.clear()
            self.meshList.addItems(self.mayaToUE.meshes)
        else:
            QMessageBox().warning(self, "Warning", msg)

    def MeshListSelectionChanged(self):
        mc.select(cl=True)
    
        for item in self.meshList.selectedItems():
            mc.select(item.text(), add=True)
    
    def AddUnrealRootBtnClicked(self):
        success, msg = self.mayaToUE.TryAddUnrealRootJnt()
        if success:
            self.jointLineEdit.setText(self.mayaToUE.rootJnt)
        else:
            QMessageBox().warning(self, "warning", msg)


    def SetSelectedAsRootBtnClicked(self):
        success, msg = self.mayaToUE.SetSelectedAsRootJnt()
        if success:
            self.jointLineEdit.setText(self.mayaToUE.rootJnt)
        else:
            QMessageBox().warning(self, "Warning", msg)

mayaToUEWidget = MayaToUEWidget()
mayaToUEWidget.show()