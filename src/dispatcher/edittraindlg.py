import wx
import logging

from dispatcher.losttrains import LostTrainsDlg
from dispatcher.trainhistory import TrainHistoryDlg
from dispatcher.preload import PreloadedTrainsDlg

MAXSTEPS = 9
BUTTONSIZE = (120, 40)


class EditTrainDlg(wx.Dialog):
	def __init__(self, parent, train, block, locos, trainRoster, engineers, activeTrains, atcFlag, arFlag, dispatcherFlag, lostTrains, trainHistory, preloadedTrains, dx, dy):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Edit Train Details", pos=(dx, dy))
		self.parent = parent
		self.Bind(wx.EVT_CLOSE, self.onCancel)

		self.train = train
		self.activeTrains = activeTrains
		self.atcFlag = atcFlag
		self.arFlag = arFlag

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		name = train.Name()
		loco = train.Loco()
		self.name = name
		atc = train.ATC()
		ar = train.AR()
		self.block = block
		
		self.startingEast = train.IsEast()
		self.templateTrain = train.TemplateTrain()

		self.locos = locos
		self.trainRoster = trainRoster
		self.noEngineer = "<none>"
		self.engineers = [self.noEngineer] + sorted(engineers)
		self.lostTrains = lostTrains
		self.trainHistory = trainHistory
		self.preloadedTrains = preloadedTrains
		
		locoList  = sorted(list(locos.keys()), key=self.BuildLocoKey)
		self.trainList = sorted(list(trainRoster.keys()))
		self.trainsWithSeq = [k for k in self.trainList if "sequence" in self.trainRoster[k] and len(self.trainRoster[k]["sequence"]) > 0 and self.trainRoster[k]["template"] is None]

		font = wx.Font(wx.Font(16, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Monospace"))

		lblTrain = wx.StaticText(self, wx.ID_ANY, "Train:", size=(120, -1))
		lblTrain.SetFont(font)
		self.cbTrainID = wx.ComboBox(self, wx.ID_ANY, name,
					choices=self.trainList,
					style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER, size=(120, -1))
		self.cbTrainID.SetFont(font)

		self.cbAssignRoute = wx.CheckBox(self, wx.ID_ANY, "Route")
		self.cbAssignRoute.SetFont(font)
		self.cbAssignRoute.SetValue(self.templateTrain is not None)

		self.cbRoute = wx.ComboBox(self, wx.ID_ANY, name,
					choices=self.trainsWithSeq,
					style=wx.CB_DROPDOWN | wx.CB_READONLY, size=(120, -1))
		self.cbRoute.SetFont(font)
		try:
			idx = self.trainsWithSeq.index(self.templateTrain)
		except ValueError:
			idx = 0
		self.cbRoute.SetSelection(idx)

		self.chosenTrain = name
		
		self.Bind(wx.EVT_COMBOBOX, self.OnTrainChoice, self.cbTrainID)
		self.Bind(wx.EVT_TEXT, self.OnTrainText, self.cbTrainID)
		self.Bind(wx.EVT_CHECKBOX, self.OnAssignRoute, self.cbAssignRoute)
		self.Bind(wx.EVT_COMBOBOX, self.OnRouteChoice, self.cbRoute)

		self.chosenLoco = loco
		
		lblLoco  = wx.StaticText(self, wx.ID_ANY, "Loco:", size=(120, -1))
		lblLoco.SetFont(font)
		self.cbLocoID = wx.ComboBox(self, wx.ID_ANY, loco,
					choices=locoList,
					style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER, size=(120, -1))
		self.cbLocoID.SetFont(font)
		
		self.Bind(wx.EVT_COMBOBOX, self.OnLocoChoice, self.cbLocoID)
		self.Bind(wx.EVT_TEXT, self.OnLocoText, self.cbLocoID)

		self.chosenEngineer = train.Engineer()
		if self.chosenEngineer is None:
			self.chosenEngineer = self.noEngineer
			
		if self.chosenEngineer not in self.engineers:
			self.engineers.append(self.chosenEngineer)
		
		lblEngineer  = wx.StaticText(self, wx.ID_ANY, "Engineer:", size=(120, -1))
		lblEngineer.SetFont(font)
		self.cbEngineer = wx.ComboBox(self, wx.ID_ANY, self.chosenEngineer,
					choices=self.engineers,
					style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER, size=(120, -1))
		self.cbEngineer.SetFont(font)
		
		self.Bind(wx.EVT_COMBOBOX, self.OnEngChoice, self.cbEngineer)
		self.Bind(wx.EVT_TEXT, self.OnEngText, self.cbEngineer)
		
		self.bClearEng = wx.Button(self, wx.ID_ANY, "Clear", size=BUTTONSIZE)
		self.Bind(wx.EVT_BUTTON, self.OnBClearEng, self.bClearEng)

		lostCt = self.lostTrains.Count()
		if lostCt > 0:
			self.bLostTrains = wx.Button(self, wx.ID_ANY, "Lost Trains", size=BUTTONSIZE)
			self.Bind(wx.EVT_BUTTON, self.OnBLostTrains, self.bLostTrains)

		self.bTrainHistory = wx.Button(self, wx.ID_ANY, "History", size=BUTTONSIZE)
		self.Bind(wx.EVT_BUTTON, self.OnBTrainHistory, self.bTrainHistory)

		if len(self.preloadedTrains) > 0:
			self.bPreloadedTrains = wx.Button(self, wx.ID_ANY, "Preloaded", size=BUTTONSIZE)
			self.Bind(wx.EVT_BUTTON, self.OnBPreloadedTrains, self.bPreloadedTrains)

		vszl = wx.BoxSizer(wx.VERTICAL)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(lblTrain, 0, wx.TOP, 5)
		hsz.AddSpacer(10)
		hsz.Add(self.cbTrainID, 0, wx.TOP, 5)
		hsz.AddSpacer(10)
		hsz.Add(self.cbAssignRoute, 0, wx.TOP, 10)
		hsz.AddSpacer(5)
		hsz.Add(self.cbRoute, 0, wx.TOP, 5)

		vszl.Add(hsz)
		
		vszl.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(lblLoco)
		hsz.AddSpacer(10)
		hsz.Add(self.cbLocoID)

		vszl.Add(hsz)
		
		vszl.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(lblEngineer, 0, wx.TOP, 5)
		hsz.AddSpacer(10)
		hsz.Add(self.cbEngineer, 0, wx.TOP, 5)
		hsz.AddSpacer(20)
		hsz.Add(self.bClearEng)
		vszl.Add(hsz)

		vszl.AddSpacer(10)

		self.stDirection = wx.StaticText(self, wx.ID_ANY, "Eastbound" if train.IsEast() else "Westbound")
		self.stDirection.SetFont(font)
		vszl.Add(self.stDirection)

		vszr = wx.BoxSizer(wx.VERTICAL)

		if lostCt > 0:
			vszr.Add(self.bLostTrains)
			vszr.AddSpacer(20)

		vszr.Add(self.bTrainHistory)

		if len(self.preloadedTrains) > 0:
			vszr.AddSpacer(20)
			vszr.Add(self.bPreloadedTrains)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(vszl)
		hsz.AddSpacer(20)
		hsz.Add(vszr)

		vsz.Add(hsz)

		vsz.AddSpacer(10)
		self.cbATC = None
		if self.atcFlag or self.arFlag:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			
			if self.atcFlag:
				self.cbATC = wx.CheckBox(self, wx.ID_ANY, "ATC")
				self.cbATC.SetFont(font)
				self.cbATC.SetValue(atc)
				hsz.Add(self.cbATC)
				self.cbATC.Enable(self.chosenLoco != "??")
				
			if self.atcFlag and self.arFlag:
				hsz.AddSpacer(20)
	
			if self.arFlag:
				self.cbAR = wx.CheckBox(self, wx.ID_ANY, "Auto Router")
				self.cbAR.SetFont(font)
				self.cbAR.SetValue(ar)
				hsz.Add(self.cbAR)
				
			vsz.AddSpacer(20)
			vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(20)
		self.stDescr = wx.StaticText(self, wx.ID_ANY, "", size=(600, -1))
		self.stDescr.SetFont(font)		
		vsz.Add(self.stDescr)
			
		vsz.AddSpacer(20)
		self.stFlags = wx.StaticText(self, wx.ID_ANY, "", size=(600, -1))
		self.stFlags.SetFont(font)
		vsz.Add(self.stFlags)

		vsz.AddSpacer(20)
		self.stTrainInfo = []
		for _ in range(MAXSTEPS):
			st = wx.StaticText(self, wx.ID_ANY, "", size=(600, -1))
			st.SetFont(font)
			vsz.Add(st)
			self.stTrainInfo.append(st)
			
		vsz.AddSpacer(30)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BUTTONSIZE)
		self.bOK.SetDefault()
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BUTTONSIZE)

		bsz = wx.BoxSizer(wx.HORIZONTAL)
		bsz.Add(self.bOK)
		bsz.AddSpacer(30)
		bsz.Add(self.bCancel)

		self.Bind(wx.EVT_BUTTON, self.onOK, self.bOK)
		self.Bind(wx.EVT_BUTTON, self.onCancel, self.bCancel)
		vsz.Add(bsz, 0, wx.ALIGN_CENTER)

		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		self.CenterOnScreen()
		
		self.ShowTrainLocoDesc()

	@staticmethod
	def BuildLocoKey(lid):
		return int(lid)
		
	def OnLocoChoice(self, evt):
		self.chosenLoco = evt.GetString()
		if self.cbATC is not None:
			self.cbATC.Enable(self.chosenLoco != "??")
		self.ShowTrainLocoDesc()

	def OnLocoText(self, evt):
		lid = evt.GetString()
		pos = self.cbLocoID.GetInsertionPoint()
		self.cbLocoID.ChangeValue(lid)
		self.cbLocoID.SetInsertionPoint(pos)
			
		self.chosenLoco = lid
		if self.cbATC is not None:
			self.cbATC.Enable(self.chosenLoco != "??")
		self.ShowTrainLocoDesc()
		evt.Skip()

	def OnTrainChoice(self, evt):
		self.chosenTrain = evt.GetString()
		logging.debug("Train choice: %s" % self.chosenTrain)
		if self.chosenTrain in self.trainRoster:
			logging.debug("It's in the roster")
			tr = self.trainRoster[self.chosenTrain]
			self.startingEast = tr["eastbound"]
			logging.debug("and it's starting direction os %s" % str(self.startingEast))
		else:
			self.startingEast = None
			logging.debug("It's NOT in the roster")

		self.ShowTrainLocoDesc()

	def OnTrainText(self, evt):
		nm = evt.GetString().upper()
		pos = self.cbTrainID.GetInsertionPoint()
		self.cbTrainID.ChangeValue(nm)
		self.cbTrainID.SetInsertionPoint(pos)
		self.chosenTrain = nm
		self.ShowTrainLocoDesc()
		evt.Skip()

	def OnAssignRoute(self, _):
		if self.cbAssignRoute.IsChecked():
			self.cbRoute.Enable(True)
			self.templateTrain = self.trainsWithSeq[0]
			self.cbRoute.SetSelection(0)
		else:
			self.cbRoute.Enable(False)
			self.templateTrain = None

	def OnRouteChoice(self, evt):
		self.templateTrain = evt.GetString()
		self.ShowTrainLocoDesc()

	def OnEngChoice(self, evt):
		self.chosenEngineer = evt.GetString()

	def OnEngText(self, evt):
		nm = evt.GetString()
		pos = self.cbEngineer.GetInsertionPoint()
		self.cbEngineer.ChangeValue(nm)
		self.cbEngineer.SetInsertionPoint(pos)
		self.chosenEngineer = nm
		evt.Skip()
		
	def OnBClearEng(self, _):
		self.chosenEngineer = self.noEngineer
		self.cbEngineer.SetValue(self.noEngineer)

	def OnBLostTrains(self, _):
		trname = ""
		dlg = LostTrainsDlg(self, self.lostTrains)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			trname = dlg.GetResult()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		tr = self.lostTrains.GetTrain(trname)
		if tr is None:
			self.parent.PopupEvent("Unable to identify lost train")
			return

		loco, engineer, east, _, route = tr
		self.FillInTrainFields(trname, loco, engineer, east, route)

	def OnBTrainHistory(self, _):
		trname = ""
		dlg = TrainHistoryDlg(self, self.trainHistory)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			trname = dlg.GetResult()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		tr = self.trainHistory.GetTrain(trname)
		if tr is None:
			self.parent.PopupEvent("Unable to identify lost train")
			return

		loco = tr["loco"]
		engineer = tr["engineer"]
		east = tr["east"]
		route = tr["route"]
		self.FillInTrainFields(trname, loco, engineer, east, route)

	def OnBPreloadedTrains(self, _):
		tr = None
		dlg = PreloadedTrainsDlg(self, self.preloadedTrains)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			tr = dlg.GetResult()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		self.FillInTrainFields(tr["name"], tr["loco"], None, tr["east"], tr["route"])

	def FillInTrainFields(self, trname, loco, engineer, east, route):
		rc = wx.ID_YES
		if east != self.startingEast:
			mdlg = wx.MessageDialog(self, 'Trains are moving in opposite directions.\nPress "Yes" to proceed',
									'Opposite Directions',
									wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
			rc = mdlg.ShowModal()
			mdlg.Destroy()

		if rc == wx.ID_YES:
			self.startingEast = east
			self.cbTrainID.SetValue(trname)
			self.cbLocoID.SetValue(loco)
			self.cbEngineer.SetValue(self.noEngineer if engineer is None or engineer == "None" else engineer)

			if route is None:
				self.cbAssignRoute.SetValue(False)
				self.cbRoute.SetSelection(0)
				self.cbAssignRoute.Enable(trname not in self.trains)
				self.cbRoute.Enable(trname not in self.trains)
			else:
				if trname in self.trains:
					mdlg = wx.MessageDialog(self, "Route cannot be set for a known train: %s\nIgnoring" % trname,
											'Known Train', wx.OK | wx.ICON_ERROR)
					mdlg.ShowModal()
					mdlg.Destroy()

					self.cbAssignRoute.SetValue(False)
					self.cbRoute.SetSelection(0)
					self.cbAssignRoute.Enable(False)
					self.cbRoute.Enable(False)

				else:
					self.cbAssignRoute.Enable(True)
					self.cbRoute.Enable(True)

					try:
						idx = self.trainsWithSeq.index(route)
					except ValueError:
						mdlg = wx.MessageDialog(self, "Route is set to unknown train: %s\nIgnoring" % route, 'Unknown Route Train', wx.OK | wx.ICON_ERROR)
						mdlg.ShowModal()
						mdlg.Destroy()
						idx = -1

					if idx >= 0:
						self.cbAssignRoute.SetValue(True)
						self.templateTrain = self.trainsWithSeq[idx]
						self.cbRoute.SetSelection(idx)
					else:
						self.cbAssignRoute.SetValue(False)
						self.templateTrain = None
						self.cbRoute.SetSelection(0)

			self.ShowTrainLocoDesc()

	def ShowTrainLocoDesc(self):
		if self.chosenLoco in self.locos and self.locos[self.chosenLoco]["desc"] is not None:
			self.stDescr.SetLabel(self.locos[self.chosenLoco]["desc"])
		else:
			self.stDescr.SetLabel("")
			
		if self.chosenTrain in self.trainRoster:
			tr = self.trainRoster[self.chosenTrain]
			try:
				self.templateTrain = tr["template"]
			except KeyError:
				self.templateTrain = None

			try:
				idx = self.trainsWithSeq.index(self.templateTrain)
			except ValueError:
				idx = -1
			self.cbRoute.SetSelection(min(idx, 0))

			self.cbAssignRoute.Enable(False)
			self.cbAssignRoute.SetValue(self.templateTrain is not None)
			self.cbRoute.Enable(False)
			try:
				tx = self.trainsWithSeq.index(self.templateTrain)
			except ValueError:
				self.templateTrain = None
				tx = wx.NOT_FOUND

			self.cbRoute.SetSelection(tx)

			self.ShowRouteDetails(tr["tracker"])

			details = "Eastbound" if self.startingEast else "Westbound"
			if tr["cutoff"]:
				details += " via cutoff"
			self.stFlags.SetLabel(details)
			
		else:
			self.cbAssignRoute.Enable(True)
			self.cbRoute.Enable(self.cbAssignRoute.IsChecked())
			if self.templateTrain is not None:
				rtr = self.trains[self.templateTrain]
				self.ShowRouteDetails(rtr["tracker"])
				details = "Eastbound" if self.startingEast else "Westbound"
				if rtr["cutoff"]:
					details += " via cutoff"
				self.stFlags.SetLabel(details)
			else:
				for st in self.stTrainInfo:
					st.SetLabel("")
				self.stFlags.SetLabel("")

	def ShowRouteDetails(self, track):
		for lx in range(MAXSTEPS):
			if lx >= len(track):
				self.stTrainInfo[lx].SetLabel("")
			else:
				self.stTrainInfo[lx].SetLabel(
					"%-12.12s  %-4.4s  %s" % (track[lx][0], "(%d)" % track[lx][2], track[lx][1]))

	def onCancel(self, _):
		self.EndModal(wx.ID_CANCEL)

	def onOK(self, _):
		if self.chosenTrain != self.name and self.chosenTrain in self.activeTrains:
			blist = self.activeTrains[self.chosenTrain].GetBlockNameList()
			if len(blist) > 0:
				plural = "s\n" if len(blist) > 1 else " "
				bstr = ", ".join(blist)

				adje, adjw = self.block.GetAdjacentBlocks()
				adjacent = False
				for adj in adje, adjw:
					if adj is not None and adj.GetName() in blist:
						adjacent = True
						break

				if not adjacent:
					dlg = wx.MessageDialog(self, "Train %s already exists on the layout in block%s%s\n\nPress \"YES\" to acquire this train ID for THIS train" % (self.chosenTrain, plural, bstr),
							'Duplicate Train', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
					rc = dlg.ShowModal()
					dlg.Destroy()
					if rc == wx.ID_YES:
						self.parent.StealTrainID(self.chosenTrain)
					else:
						return
			else:
				mdlg = wx.MessageDialog(self,
							'Train does not exist in any blocks', 'No Blocks', wx.OK | wx.ICON_WARNING)
				mdlg.ShowModal()
				mdlg.Destroy()

		if self.cbAssignRoute.IsChecked():
			if self.templateTrain is not None:
				if self.startingEast != self.trainRoster[self.templateTrain]["eastbound"]:
					mdlg = wx.MessageDialog(self,  'Route is in the opposite direction from the train.\nPress "Yes" to proceed',
									'Opposite Directions',
									wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
					rc = mdlg.ShowModal()
					mdlg.Destroy()
					if rc != wx.ID_YES:
						return

		self.lostTrains.Remove(self.chosenTrain)
		self.EndModal(wx.ID_OK)

	def GetResults(self):
		t = self.chosenTrain
		l = self.chosenLoco
		e = self.chosenEngineer
		if e == self.noEngineer:
			e = None
		if self.cbAssignRoute.IsChecked():
			r = self.templateTrain
		else:
			r = None
			
		atc = False if not self.atcFlag else self.cbATC.GetValue()
		ar = False if not self.arFlag else self.cbAR.GetValue()

		return t, l, e, atc, ar, self.startingEast, r


class SortTrainBlocksDlg(wx.Dialog):
	def __init__(self, parent, tr, blocks):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.parent = parent
		self.rrblocks = blocks
		self.Bind(wx.EVT_CLOSE, self.onCancel)

		self.modified = False
		self.titleText = "Reorder Blocks for Train %s" % tr.Name()
		self.SetTitleText()

		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial"))
		stFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))

		self.dmap = {}
		self.blocks = []
		for bn in reversed(tr.Blocks()):
			blk = self.rrblocks.get(bn, None)
			if blk is None:
				bdesig = bn
			else:
				bn = blk.GetName()
				bdesig = blk.GetRouteDesignator()

			if bn == bdesig:
				self.blocks.append(bn)
			else:
				self.blocks.append(bdesig)
				self.dmap[bdesig] = bn

		self.parent.PopupAdvice("dmap = %s" % str(self.dmap))

		self.lbBlocks = wx.ListBox(self, wx.ID_ANY, choices=self.blocks, size=(160, 200))
		self.lbBlocks.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbBlocksSelect, self.lbBlocks)
		self.lbBlocks.SetSelection(0)
		self.sx = 0

		self.bUp = wx.Button(self, wx.ID_ANY, u'\u25b2' + " Up " + u'\u25b2', size=BUTTONSIZE)
		self.bUp.SetFont(stFont)
		self.Bind(wx.EVT_BUTTON, self.onBUp, self.bUp)
		self.bUp.SetToolTip("Move selected block up towards the front of the train")
		self.bUp.Enable(False)

		self.bDown = wx.Button(self, wx.ID_ANY, u'\u25bc' + " Down " + u'\u25bc', size=BUTTONSIZE)
		self.bDown.SetFont(stFont)
		self.Bind(wx.EVT_BUTTON, self.onBDown, self.bDown)
		self.bDown.SetToolTip("Move selected block down towards the rear of the train")
		self.bDown.Enable(True)

		self.bReverse = wx.Button(self, wx.ID_ANY, "Reverse", size=BUTTONSIZE)
		self.bReverse.SetFont(stFont)
		self.Bind(wx.EVT_BUTTON, self.onBReverse, self.bReverse)
		self.bReverse.SetToolTip("Reverse the block order without changing the train direction")

		vsz = wx.BoxSizer(wx.VERTICAL)

		vsz.AddSpacer(20)

		st = wx.StaticText(self, wx.ID_ANY, "Front of Train")
		st.SetFont(stFont)
		vsz.Add(st, 0, wx.LEFT, 20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.lbBlocks)
		hsz.AddSpacer(20)

		btnsz = wx.BoxSizer(wx.VERTICAL)
		btnsz.AddSpacer(20)
		btnsz.Add(self.bUp)
		btnsz.AddSpacer(30)
		btnsz.Add(self.bReverse)
		btnsz.AddSpacer(30)
		btnsz.Add(self.bDown)
		btnsz.AddSpacer(20)

		hsz.Add(btnsz, 0, wx.ALIGN_CENTER_VERTICAL)

		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Rear of Train")
		st.SetFont(stFont)
		vsz.Add(st, 0, wx.LEFT, 20)

		vsz.AddSpacer(20)

		btnsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BUTTONSIZE)
		self.Bind(wx.EVT_BUTTON, self.onBOK, self.bOK)

		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BUTTONSIZE)
		self.Bind(wx.EVT_BUTTON, self.onCancel, self.bCancel)

		btnsz.Add(self.bOK)
		btnsz.AddSpacer(30)
		btnsz.Add(self.bCancel)

		vsz.Add(btnsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()

	def SetTitleText(self):
		title = self.titleText + (" * " if self.modified else "")
		self.SetTitle(title)

	def SetModified(self, flag=True):
		if flag != self.modified:
			self.modified = flag
			self.SetTitleText()

	def onLbBlocksSelect(self, _):
		self.sx = self.lbBlocks.GetSelection()
		self.EnableButtons()

	def EnableButtons(self):
		self.bUp.Enable(self.sx > 0)
		self.bDown.Enable(self.sx < (len(self.blocks)-1))

	def onBUp(self, _):
		s1 = self.sx
		s0 = s1 - 1

		self.blocks[s0], self.blocks[s1] = self.blocks[s1], self.blocks[s0]
		self.lbBlocks.SetItems(self.blocks)
		self.sx = s0
		self.lbBlocks.SetSelection(s0)
		self.EnableButtons()
		self.SetModified()

	def onBDown(self, _):
		s0 = self.sx
		s1 = s0 + 1

		self.blocks[s0], self.blocks[s1] = self.blocks[s1], self.blocks[s0]
		self.lbBlocks.SetItems(self.blocks)
		self.sx = s1
		self.lbBlocks.SetSelection(s1)
		self.EnableButtons()
		self.SetModified()

	def onBReverse(self, _):
		self.blocks = list(reversed(self.blocks))
		self.lbBlocks.SetItems(self.blocks)
		self.lbBlocks.SetSelection(0)
		self.sx = 0
		self.EnableButtons()
		self.SetModified()

	def onBOK(self, _):
		self.EndModal(wx.ID_OK if self.modified else wx.ID_EXIT)

	def onCancel(self, _):
		if self.modified:
			dlg = wx.MessageDialog(self, "All pending changes will be list if you cancel.  Press Yes to proceed",
				"Changes Pending", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)

			rc = dlg.ShowModal()
			dlg.Destroy()

			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)

	def GetResults(self):
		rv = [self.dmap.get(b, b) for b in reversed(self.blocks)]
		return rv
