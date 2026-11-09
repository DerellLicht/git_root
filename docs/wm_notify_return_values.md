WM_NOTIFY basics:

wParam = the control ID that sent it.  
lParam = a pointer to an NMHDR (or a larger struct that starts with an NMHDR) --  
always check ((NMHDR*)lParam)->code to know what you're actually looking at before casting further.
Same rule as WM_CTLCOLOR*: many notification codes expect a real return value, not just handled/not-handled. Mechanism is identical -- SetWindowLongPtr(hdlg, DWLP_MSGRESULT, value) then return TRUE.

The ones that bite people:

NM_CUSTOMDRAW (ListView/TreeView/etc.) -- the classic gotcha. It's a multi-stage conversation: you get called at CDDS_PREPAINT first, and your DWLP_MSGRESULT return there (e.g. CDRF_NOTIFYITEMDRAW) determines whether you get called again per-item. Forget to return the right flag at the right stage and your custom draw code silently never fires.
TTN_GETDISPINFO (tooltips) -- different pattern: you write your text/data directly into the NMTTDISPINFO struct through the lParam pointer, not through DWLP_MSGRESULT. Just return TRUE once you've filled it in.
LVN_ITEMCHANGING / TVN_ITEMEXPANDING -- return TRUE via DWLP_MSGRESULT to veto the change. Easy to get backwards (TRUE feels like "yes, proceed" but it means "yes, block it").
Same code from different controls -- idFrom/hwndFrom in the NMHDR matter as much as code does. Don't assume a code implies a specific control type before checking which control it came from; casting to NMLISTVIEW on data that's actually from a TreeView is a real bug, not just untidy.

That should be a solid quick-reference for the sweep.