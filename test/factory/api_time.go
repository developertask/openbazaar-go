package factory

import (
	"time"

	"github.com/developertask/openbazaar-go/repo"
)

func NewAPITime(t time.Time) *repo.APITime {
	return repo.NewAPITime(t)
}
