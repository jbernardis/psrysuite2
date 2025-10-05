import wx
from wx.lib.intctrl import IntCtrl 

from traineditor.trainsequences.nextblocklist import NextBlockListCtrl
from traineditor.trainsequences.blocksequence import BlockSequenceListCtrl
from traineditor.trainsequences.editblockdlg import EditBlockDlg


class TrainDlg(wx.Dialog):
	def __init__(self, parent, train, layout):
		self.parent = parent
		
		wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)

		self.layout = layout
		self.trainObject = train		
		self.trainid = train.GetTrainID()
		self.locoid = 7000
		self.east = train.IsEast()
		
		self.blockList = [x for x in train.GetSteps()]
		
		self.title = "Edit Train Step Sequence Dialog"
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.availableBlocks = None

		boxStartLoc = wx.StaticBox(self, wx.ID_ANY, " Starting Location ")

		self.chStartBlock = wx.Choice(boxStartLoc, wx.ID_ANY, choices=[], size=(60, -1))
		self.chStartSubBlock = wx.Choice(boxStartLoc, wx.ID_ANY, choices=[], size=(60, -1))
		self.chStartSubBlock.Enable(False)
		
		#self.tcStartBlockTime = wx.TextCtrl(boxStartLoc, wx.ID_ANY, "5000", size=(60, -1), style=wx.TE_RIGHT)
		ic = IntCtrl(boxStartLoc, wx.ID_ANY, size=(60, -1), style=wx.TE_RIGHT)
		ic.SetMin(0)
		ic.SetMax(99999)
		ic.SetValue(5000)
		ic.SetNoneAllowed(False)
		self.tcStartBlockTime = ic

		self.nextBlockList = NextBlockListCtrl(self)
		self.blockSequence = BlockSequenceListCtrl(self)

		self.bAdd = wx.Button(self, wx.ID_ANY, "Add >>")
		self.Bind(wx.EVT_BUTTON, self.OnBAdd, self.bAdd)
		self.bAdd.Enable(False)
		self.bDel = wx.Button(self, wx.ID_ANY, "<< Del")
		self.Bind(wx.EVT_BUTTON, self.OnBDel, self.bDel)
		self.bDel.Enable(False)

		self.bValidate = wx.Button(self, wx.ID_ANY, "Validate", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBValidate, self.bValidate)
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBCancel, self.bCancel)

		topBorder = boxStartLoc.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(10+topBorder)

		hsz = wx.BoxSizer(wx.HORIZONTAL)

		hsz.AddSpacer(20)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(wx.StaticText(boxStartLoc, wx.ID_ANY, "Block"))
		vsz.AddSpacer(5)
		vsz.Add(self.chStartBlock)
		hsz.Add(vsz)
		hsz.AddSpacer(20)
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(wx.StaticText(boxStartLoc, wx.ID_ANY, "Sub-block"))
		vsz.AddSpacer(5)
		vsz.Add(self.chStartSubBlock)
		hsz.Add(vsz)
		hsz.AddSpacer(20)
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(wx.StaticText(boxStartLoc, wx.ID_ANY, "Time"))
		vsz.AddSpacer(5)
		vsz.Add(self.tcStartBlockTime)
		hsz.Add(vsz)

		hsz.AddSpacer(20)

		bsizer.Add(hsz)
		bsizer.AddSpacer(20)

		boxStartLoc.SetSizer(bsizer)

		vszl = wx.BoxSizer(wx.VERTICAL)
		vszl.AddSpacer(20)
		vszl.Add(boxStartLoc)
		vszl.AddSpacer(20)
		vszl.Add(wx.StaticText(self, wx.ID_ANY, "Next Available Blocks"), 1, wx.ALIGN_CENTER_HORIZONTAL)
		vszl.AddSpacer(10)
		vszl.Add(self.nextBlockList)
		vszm = wx.BoxSizer(wx.VERTICAL)
		vszm.AddSpacer(220)
		vszm.Add(self.bAdd, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszm.AddSpacer(10)
		vszm.Add(self.bDel, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszm.AddSpacer(20)

		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(20)
		vszr.Add(wx.StaticText(self, wx.ID_ANY, "Blocks in Train Route"), 1, wx.ALIGN_CENTER_HORIZONTAL)
		vszr.AddSpacer(10)
		vszr.Add(self.blockSequence)
		vszr.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vszl)
		hsz.AddSpacer(20)
		hsz.Add(vszm)
		hsz.AddSpacer(20)
		hsz.Add(vszr)
		hsz.AddSpacer(20)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(hsz)
		vsz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.bValidate)
		hsz.AddSpacer(50)
		hsz.Add(self.bOK)
		hsz.AddSpacer(20)
		hsz.Add(self.bCancel)
		
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Fit()
		self.Layout()

		self.startBlock = None
		self.startSubBlock = None
		self.blockList = []
		wx.CallAfter(self.Initialize)

	def ShowTitle(self):
		titleString = "%s: %s" % (self.title, self.trainid)
		if self.modified:
			titleString += " *"

		self.SetTitle(titleString)

	def Initialize(self):
		self.modified = False
		self.ShowTitle()

		self.blockList = self.layout.GetBlocks()
		self.chStartBlock.SetItems(self.blockList)
		
		steps = self.trainObject.GetSteps()
		if len(steps) == 0:
			self.startBlock = self.blockList[0]
			self.startSubBlock = None
			self.chStartBlock.SetSelection(0)
			self.tcStartBlockTime.SetValue(5000)
			self.GetAvailableBlocks(self.startBlock)
			self.nextBlockList.SetBlocks(self.availableBlocks)
			self.SetSubBlockChoices(self.startBlock, None)
		else:	
			self.startBlock = self.trainObject.GetStartBlock()
			startSubBlock = self.trainObject.GetStartSubBlock()
			try:
				bx = self.blockList.index(self.startBlock)
				self.chStartBlock.SetSelection(bx)
			except ValueError:
				self.chStartBlock.SetSelection(0)
				
			self.tcStartBlockTime.SetValue(self.trainObject.GetStartBlockTime())

			lastBlock = self.startBlock				
			for step in self.trainObject.GetSteps():		
				self.blockSequence.AddBlock(step)
				lastBlock = step["block"]
				
			self.GetAvailableBlocks(lastBlock)
			self.nextBlockList.SetBlocks(self.availableBlocks)
				
			self.SetSubBlockChoices(self.startBlock, startSubBlock)

			
		self.Bind(wx.EVT_CHOICE, self.OnChStartBlock, self.chStartBlock)
		self.Bind(wx.EVT_CHOICE, self.OnChStartSubBlock, self.chStartSubBlock)
		
	def SetModified(self, flag=True):
		self.modified = flag
		self.ShowTitle()

	def OnChStartBlock(self, event):
		self.SetModified()
		self.startBlock = event.GetString()
		self.GetAvailableBlocks(self.startBlock)
		self.nextBlockList.SetBlocks(self.availableBlocks)
		self.SetSubBlockChoices(self.startBlock, None)
		
	def SetSubBlockChoices(self, blk, subblk):
		subBlocks = self.layout.GetSubBlocks(blk)
		if len(subBlocks) == 0:
			self.startSubBlock = None
			self.chStartSubBlock.Enable(False)
		else:
			self.chStartSubBlock.Enable(True)
			self.chStartSubBlock.SetItems(subBlocks)
			self.startSubBlock = subblk
			try:
				bx = subBlocks.index(subblk)
				self.chStartSubBlock.SetSelection(bx)
				self.startSubBlock = subblk
			except ValueError:
				self.chStartSubBlock.SetSelection(0)
				self.startSubBlock = subBlocks[0]

	def OnChStartSubBlock(self, event):
		self.SetModified()
		self.startSubBlock = event.GetString()

	def reportNonEmpty(self, seqNotEmpty):
		self.bDel.Enable(seqNotEmpty)
		self.bGenSim.Enable(seqNotEmpty)
		self.bGenAR.Enable(seqNotEmpty)
		
	def reportItemActivated(self, idx):
		rv = self.blockSequence.GetBlock(idx)
		if rv is None:
			return

		dlg = EditBlockDlg(self, rv["time"], rv["trigger"])
		rc = dlg.ShowModal()
		
		if rc == wx.ID_OK:
			ttime, trigger = dlg.GetResults()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return
		
		rv["trigger"] = trigger
		rv["time"] = ttime
		self.SetModified(True)
		self.blockSequence.SetBlock(idx, rv)

	def reportSelection(self, tx, activate):
		if tx is None:
			self.bAdd.Enable(False)
		else:
			if activate:
				self.SelectNextBlock(tx)
			else:
				self.bAdd.Enable(True)

	def OnBAdd(self, _):
		tx = self.nextBlockList.GetSelection()
		if tx is not None:
			self.SelectNextBlock(tx)

	def SelectNextBlock(self, tx):
		self.SetModified()
		self.chStartBlock.Enable(False)
		self.chStartSubBlock.Enable(False)
		nextStep = {
			"block":   self.availableBlocks[tx][0],
			"signal":  self.availableBlocks[tx][1],
			"os":      self.availableBlocks[tx][2],
			"route":   self.availableBlocks[tx][3],
			"time":    5000,
			"trigger": "Front"
		}

		self.blockSequence.AddBlock(nextStep)
		self.GetAvailableBlocks(nextStep["block"])
		self.nextBlockList.SetBlocks(self.availableBlocks)

	def OnBDel(self, _):
		self.SetModified()
		r = self.blockSequence.DelBlock()
		if r is None:
			self.bDel.Enable(False)
			self.bAdd.Enable(False)
			self.chStartBlock.Enable(True)
			self.chStartSubBlock.Enable(True)
			self.GetAvailableBlocks(self.startBlock)
			self.nextBlockList.SetBlocks(self.availableBlocks)
		else:
			self.GetAvailableBlocks(r["block"])
			self.nextBlockList.SetBlocks(self.availableBlocks)
			
	def OnBValidate(self, _):
		blk = self.startBlock
		steps = self.blockSequence.GetBlocks()
		badTransitions = self.parent.validateSequence(blk, steps)

		title = "Validation Results for Train %s" % self.trainid		
		if len(badTransitions) == 0:
			dlg = wx.MessageDialog(self, 'Block sequence is correct!',
					title, wx.OK | wx.ICON_INFORMATION)
		else:
			msg = "The following transitions are incorrect:\n " + "\n ".join(badTransitions)
			dlg = wx.MessageDialog(self, msg,
					title, wx.OK | wx.ICON_ERROR)
			
		dlg.ShowModal()
		dlg.Destroy()
			
		
	def GetAvailableBlocks(self, blk):
		self.availableBlocks = []
		if blk is None:
			return
		rteList = self.layout.GetRoutesForBlock(blk)
		for r in rteList:
			e = self.layout.GetRouteEnds(r)
			s = self.layout.GetRouteSignals(r)
			os = self.layout.GetRouteOS(r)
			if e[0] == blk:
				self.availableBlocks.append([e[1], s[0], os, r])
			elif e[1] == blk:
				self.availableBlocks.append([e[0], s[1], os, r])
		if blk == "F10":
			self.availableBlocks.append(["R10", None, None, None])
		elif blk == "R10":
			self.availableBlocks.append(["F10", None, None, None])

	def GetResults(self):
		return {"startblock": self.startBlock, "startsubblock": self.startSubBlock, "time": self.tcStartBlockTime.GetValue(), "steps": self.blockSequence.GetBlocks()}

	def OnClose(self, _):
		self.DoCancel()
		
	def OnBOK(self, _):
		self.EndModal(wx.ID_OK)
		
	def OnBCancel(self, _):
		self.DoCancel()
		
	def DoCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Train steps have been modified.\nAre you sure you want to cancel?\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		self.EndModal(wx.ID_CANCEL)
