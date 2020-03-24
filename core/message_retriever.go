package core

import (
	"github.com/developertask/openbazaar-go/net/retriever"
)

// StartMessageRetriever will collect the required options from the
// developertaskNode and begin the MessageRetriever in the background
func (n *developertaskNode) StartMessageRetriever() {
	config := net.MRConfig{
		Db:        n.Datastore,
		IPFSNode:  n.IpfsNode,
		DHT:       n.DHT,
		BanManger: n.BanManager,
		Service:   n.Service,
		PrefixLen: 14,
		PushNodes: n.PushNodes,
		Dialer:    n.TorDialer,
		SendAck:   n.SendOfflineAck,
		SendError: n.SendError,
	}
	n.MessageRetriever = net.NewMessageRetriever(config)
	go n.MessageRetriever.Run()
}

// WaitForMessageRetrieverCompletion will return once the MessageRetriever
// has finished processing messages
func (n *developertaskNode) WaitForMessageRetrieverCompletion() {
	if n.MessageRetriever == nil {
		return
	}
	n.MessageRetriever.Wait()
}
