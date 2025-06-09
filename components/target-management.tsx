"use client"

import { useEffect, useState } from "react"
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

export function TargetManagement() {
  const [targets, setTargets] = useState<Target[]>([])
  const [newTarget, setNewTarget] = useState({ domain: "", program: "" })
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Hedefleri API'den çek
  const fetchTargets = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("/api/targets")
      if (!res.ok) throw new Error("Failed to fetch targets")
      const data = await res.json()
      setTargets(data)
    } catch (e: any) {
      setError(e.message || "Unknown error")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTargets()
  }, [])

  // Hedef ekle
  const addTarget = async () => {
    if (newTarget.domain && newTarget.program) {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch("/api/targets", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...newTarget }),
        })
        if (!res.ok) throw new Error("Failed to add target")
        setNewTarget({ domain: "", program: "" })
        setIsDialogOpen(false)
        fetchTargets()
      } catch (e: any) {
        setError(e.message || "Unknown error")
      } finally {
        setLoading(false)
      }
    }
  }

  // Hedef durumunu değiştir
  const toggleTargetStatus = async (id: string, currentStatus: Target["status"]) => {
    setLoading(true)
    setError(null)
    try {
      const newStatus = currentStatus === "active" ? "paused" : "active"
      const res = await fetch(`/api/targets/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      })
      if (!res.ok) throw new Error("Failed to update target status")
      fetchTargets()
    } catch (e: any) {
      setError(e.message || "Unknown error")
    } finally {
      setLoading(false)
    }
  }

  // Hedef sil
  const deleteTarget = async (id: string) => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`/api/targets/${id}`, { method: "DELETE" })
      if (!res.ok) throw new Error("Failed to delete target")
      fetchTargets()
    } catch (e: any) {
      setError(e.message || "Unknown error")
    } finally {
      setLoading(false)
    }
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
              <Button onClick={addTarget} disabled={loading}>
                Add Target
              </Button>
            </DialogFooter>
            {error && <div className="text-red-500 text-sm">{error}</div>}
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Active Targets</CardTitle>
          <CardDescription>Monitor and control your reconnaissance targets</CardDescription>
        </CardHeader>
        <CardContent>
          {loading && <div className="text-muted-foreground">Loading...</div>}
          {error && <div className="text-red-500 text-sm">{error}</div>}
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
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toggleTargetStatus(target.id, target.status)}
                        disabled={loading}
                      >
                        {target.status === "active" ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                      </Button>
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => deleteTarget(target.id)}
                        disabled={loading}
                      >
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