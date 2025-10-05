import wx
from wx.lib.intctrl import IntCtrl

		
class EditBlockDlg(wx.Dialog):
	def __init__(self, parent, ttime, trigger):
		self.parent = parent
		
		wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)

		self.ttime = ttime
		self.trigger = trigger
		
		self.modified = False
		
		self.title = "Edit Step"
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.icTTime = IntCtrl(self, wx.ID_ANY, size=(60, -1), style=wx.TE_RIGHT)
		self.icTTime.SetMin(0)
		self.icTTime.SetMax(99999)
		self.icTTime.SetValue(self.ttime)
		self.icTTime.SetNoneAllowed(False)
		self.Bind(wx.EVT_TEXT, self.OnText, self.icTTime)
		
		self.triggerValues = ["Front", "Rear"]
		self.rbTrigger = wx.RadioBox(self, wx.ID_ANY, "Trigger Point", choices=self.triggerValues)
		self.rbTrigger.SetSelection(0)
		for i in range(len(self.triggerValues)):
			if self.trigger == self.triggerValues[i]:
				self.rbTrigger.SetSelection(i)
				break

		self.Bind(wx.EVT_RADIOBOX, self.OnTrigger, self.rbTrigger)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBCancel, self.bCancel)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Block Traversal Time:"))
		hsz.Add(self.icTTime)
		vsz.Add(hsz)
		
		vsz.AddSpacer(20)
		
		vsz.Add(self.rbTrigger, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(40)

		bsz = wx.BoxSizer(wx.HORIZONTAL)
		bsz.Add(self.bOK)
		bsz.AddSpacer(20)
		bsz.Add(self.bCancel)
		
		vsz.Add(bsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
				
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Fit()
		self.Layout()

		wx.CallAfter(self.Initialize)

	def ShowTitle(self):
		titleString = "%s" % self.title
		if self.modified:
			titleString += " *"

		self.SetTitle(titleString)

	def Initialize(self):
		self.modified = False
		self.ShowTitle()
		
	def OnText(self, _):
		self.SetModified()
		
	def OnTrigger(self, _):
		self.SetModified()
		
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
				self.startSubBlock = None

	def OnChStartSubBlock(self, event):
		self.SetModified()
		self.startSubBlock = event.GetString()
				
	def GetResults(self):
		tx = self.rbTrigger.GetSelection()
		return self.icTTime.GetValue(), self.triggerValues[tx]

	def OnClose(self, _):
		self.DoCancel()
		
	def OnBOK(self, _):
		self.EndModal(wx.ID_OK)
		
	def OnBCancel(self, _):
		self.DoCancel()
		
	def DoCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Data has been modified.\nAre you sure you want to cancel?\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		self.EndModal(wx.ID_CANCEL)

