import os
import wx

from traineditor.engineers.engineers import Engineers


wildcardTxt = "TXT file (*.txt)|*.txt|"	 \
				"All files (*.*)|*.*"

BTNSZ = (120, 46)

class ManageEngineersDlg(wx.Dialog):
	def __init__(self, parent, rrserver):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Manage Engineers")
		self.parent = parent
		self.rrserver = rrserver

		self.titleString = "Manage Engineers"
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
	
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial"))
		
		self.eng = Engineers(rrserver)
		self.engineers = self.eng.getEngineerList()
		
		self.lbEngineers = wx.ListBox(self, wx.ID_ANY, choices=self.engineers, size=(160, 200))
		self.lbEngineers.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbActiveSelect, self.lbEngineers)
		#self.Bind(wx.EVT_LISTBOX_DCLICK, self.bLeftPressed, self.lbEngineers)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(self.lbEngineers, 0, wx.ALIGN_CENTER_VERTICAL)
		hsz.AddSpacer(20)
		
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.AddSpacer(20)
				
		self.bAddEng = wx.Button(self, wx.ID_ANY, "Add", size=BTNSZ)
		self.bAddEng.SetFont(btnFont)
		self.bAddEng.SetToolTip("Add a new engineer")
		sz.Add(self.bAddEng, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.Bind(wx.EVT_BUTTON, self.bAddEngPressed, self.bAddEng)
		
		sz.AddSpacer(20)
		
		self.bDelEng = wx.Button(self, wx.ID_ANY, "Delete", size=BTNSZ)
		self.bDelEng.SetFont(btnFont)
		self.bDelEng.SetToolTip("Delete the selected engineer")
		sz.Add(self.bDelEng)
		self.Bind(wx.EVT_BUTTON, self.bDelEngPressed, self.bDelEng)
		self.bDelEng.Enable(False)

		sz.AddSpacer(20)
		hsz.Add(sz, 0, wx.ALIGN_CENTER_VERTICAL)
		hsz.AddSpacer(20)
		
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)		
		vsz.AddSpacer(20)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		
		sz.AddSpacer(20)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=BTNSZ)
		self.bSave.SetFont(btnFont)
		self.bSave.SetToolTip("Save the list of engineers and remain on the dialog box")
		sz.Add(self.bSave)
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
				
		sz.AddSpacer(20)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.bOK.SetToolTip("Save the engineers (if needed) and exit the dialog box")
		sz.Add(self.bOK)
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		
		sz.AddSpacer(20)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.bCancel.SetToolTip("Exit the dialog box discarding any pending changes")
		sz.Add(self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)

		sz.AddSpacer(20)
		
		vsz.Add(sz, 0, wx.ALIGN_CENTER_HORIZONTAL)		
		vsz.AddSpacer(20)
		
		self.setModified(False)
		
		self.SetSizer(vsz)
		self.Layout()
		self.Fit()

		self.setTitle()

	def setTitle(self):
		title = self.titleString
		if self.modified:
			title += " *"

		self.SetTitle(title)
		
	def setModified(self, flag=True):
		self.modified = flag
		self.setTitle()
		
	def onLbActiveSelect(self, _):
		sx = self.lbEngineers.GetSelection()
		self.bDelEng.Enable(sx != wx.NOT_FOUND)

	def bAddEngPressed(self, _):
		dlg = wx.TextEntryDialog(
				self, 'Enter Name of new engineer',
				'Add Engineer', '')

		rc = dlg.ShowModal()
		
		if rc == wx.ID_OK:
			eng = dlg.GetValue()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		if eng in self.engineers:
			dlg = wx.MessageDialog(self, "Engineer \"%s\" is already in the list" % eng, 
					"Duplicate Name", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return
		
		self.engineers.append(eng)
		self.engineers = sorted(self.engineers)
		self.eng.add(eng)
		
		self.lbEngineers.SetItems(self.engineers)
		ix = self.engineers.index(eng)
		self.lbEngineers.SetSelection(ix)		
		self.setModified()
		
	def bDelEngPressed(self, _):
		sx = self.lbEngineers.GetSelection()
		if sx == wx.NOT_FOUND:
			return
		
		eng = self.lbEngineers.GetString(sx)
		self.lbEngineers.Delete(sx)
		self.eng.delete(eng)
		self.engineers = self.eng.getEngineerList()
		self.setModified()
		if sx >= len(self.engineers):
			sx = len(self.engineers) -1
		self.lbEngineers.SetSelection(sx)		

	def bSavePressed(self, _):
		self.eng.save()
		self.setModified(False)
		dlg = wx.MessageDialog(self, 'Engineer list has been saved', 'Data Saved', wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()

	def bOKPressed(self, _):
		if self.modified:
			self.eng.save()
		self.EndModal(wx.ID_OK)
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Engineer list has been changed\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)
