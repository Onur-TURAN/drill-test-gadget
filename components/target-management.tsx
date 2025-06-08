"use client"

import { useState } from "react"
import { Plus, Play, Pause, Trash2, Eye } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

interface Target {
  id: string
  domain: string
  program: string
  status: "active" | "paused" | "completed"
  lastScan: string
  vulnCount: number
}

const mockTargets: Target[] = [
  {
    id: "1",
    domain: "example.com",
    program: "Example Bug Bounty",
    status: "active",
    lastScan: "2024-01-15 14:30",
    vulnCount: 3,
  },
  {
    id: "2",
    domain: "test.org",
    program: "Test Security Program",
    status: "paused",
    lastScan: "2024-01-14 09:15",
    vulnCount: 1,
  },
]

export function TargetManagement() {
  const [targets, setTargets] = useState<Target[]>(mockTargets)
  const [newTarget, setNewTarget] = useState({ domain: "", program: "" })
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const addTarget = () => {
    if (newTarget.domain && newTarget.program) {
      const target: Target = {
        id: Date.now().toString(),
        domain: newTarget.domain,
        program: newTarget.program,
        status: "paused",
        lastScan: "Never",
        vulnCount: 0,
      }
      setTargets([...targets, target])
      setNewTarget({ domain: "", program: "" })
      setIsDialogOpen(false)
    }
  }

  const toggleTargetStatus = (id: string) => {
    setTargets(
      targets.map((target) =>
        target.id === id ? { ...target, status: target.status === "active" ? "paused" : "active" } : target,
      ),
    )
  }

  const deleteTarget = (id: string) => {
    setTargets(targets.filter((target) => target.id !== id))
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      active: "bg-green-500",
      paused: "bg-yellow-500",
      completed: "bg-blue-500",
    }
    return <Badge className={variants[status as keyof typeof variants]}>{status}</Badge>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Target Management</h2>
          <p className="text-muted-foreground">Manage your bug bounty targets and programs</p>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Target
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Target</DialogTitle>
              <DialogDescription>
                Add a new target domain for reconnaissance and vulnerability scanning.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="domain">Domain</Label>
                <Input
                  id="domain"
                  placeholder="example.com"
                  value={newTarget.domain}
                  onChange={(e) => setNewTarget({ ...newTarget, domain: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="program">Bug Bounty Program</Label>
                <Input
                  id="program"
                  placeholder="Example Bug Bounty Program"
                  value={newTarget.program}
                  onChange={(e) => setNewTarget({ ...newTarget, program: e.target.value })}
                />
              </div>
            </div>
            <DialogFooter>
              <Button onClick={addTarget}>Add Target</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Active Targets</CardTitle>
          <CardDescription>Monitor and control your reconnaissance targets</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Domain</TableHead>
                <TableHead>Program</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last Scan</TableHead>
                <TableHead>Vulnerabilities</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {targets.map((target) => (
                <TableRow key={target.id}>
                  <TableCell className="font-medium">{target.domain}</TableCell>
                  <TableCell>{target.program}</TableCell>
                  <TableCell>{getStatusBadge(target.status)}</TableCell>
                  <TableCell>{target.lastScan}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{target.vulnCount}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm" onClick={() => toggleTargetStatus(target.id)}>
                        {target.status === "active" ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                      </Button>
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => deleteTarget(target.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
