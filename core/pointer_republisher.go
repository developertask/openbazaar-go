package core

import (
	"github.com/developertask/openbazaar-go/net/repointer"
)

// StartPointerRepublisher - setup republisher for IPNS
func (n *developertaskNode) StartPointerRepublisher() {
	n.PointerRepublisher = net.NewPointerRepublisher(n.DHT, n.Datastore, n.PushNodes, n.IsModerator)
	go n.PointerRepublisher.Run()
}
