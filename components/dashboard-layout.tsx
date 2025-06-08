"use client"

import type React from "react"
import { Activity, Bug, Database, FileText, Home, Search, Shield, Target, Terminal } from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"

const menuItems = [
  {
    title: "Dashboard",
    icon: Home,
    url: "/",
  },
  {
    title: "Targets",
    icon: Target,
    url: "/targets",
  },
  {
    title: "Reconnaissance",
    icon: Search,
    url: "/recon",
  },
  {
    title: "Vulnerabilities",
    icon: Bug,
    url: "/vulns",
  },
  {
    title: "Reports",
    icon: FileText,
    url: "/reports",
  },
  {
    title: "CVE Database",
    icon: Database,
    url: "/cve",
  },
  {
    title: "Tools",
    icon: Terminal,
    url: "/tools",
  },
  {
    title: "Monitoring",
    icon: Activity,
    url: "/monitoring",
  },
]

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        <Sidebar>
          <SidebarHeader className="p-4">
            <div className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-red-500" />
              <span className="font-bold text-lg">BugBounty Lab</span>
            </div>
          </SidebarHeader>
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupLabel>Navigation</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {menuItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton asChild>
                        <a href={item.url} className="flex items-center gap-2">
                          <item.icon className="h-4 w-4" />
                          <span>{item.title}</span>
                        </a>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
        </Sidebar>

        <div className="flex-1 flex flex-col">
          <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex h-14 items-center px-4">
              <SidebarTrigger />
              <div className="ml-auto flex items-center space-x-4">
                <Button variant="outline" size="sm">
                  Emergency Stop
                </Button>
              </div>
            </div>
          </header>
          <main className="flex-1 p-6">{children}</main>
        </div>
      </div>
    </SidebarProvider>
  )
}
