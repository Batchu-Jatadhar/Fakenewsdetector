"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { getUser, isAuthenticated, logout, hasRole } from "@/lib/auth";
import type { User } from "@/types";

export default function Navbar() {
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (isAuthenticated()) {
      setUser(getUser());
    }
  }, []);

  const navLink = (href: string, label: string) => (
    <Link
      href={href}
      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
        pathname === href
          ? "bg-indigo-600 text-white"
          : "text-slate-300 hover:bg-surface-light hover:text-white"
      }`}
    >
      {label}
    </Link>
  );

  return (
    <nav className="bg-surface border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-4">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <span className="text-xl font-bold text-white">VeritasAI</span>
            </Link>

            {mounted && user && (
              <div className="hidden md:flex items-center space-x-1 ml-6">
                {navLink("/", "Analyze")}
                {navLink("/history", "History")}
                {navLink("/dashboard", "Dashboard")}
                {hasRole("analyst", "admin") && navLink("/admin", "Admin")}
              </div>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {mounted && user ? (
              <div className="flex items-center space-x-3">
                <div className="text-sm">
                  <span className="text-slate-400">{user.full_name}</span>
                  <span className="ml-2 badge bg-indigo-500/20 text-indigo-400 text-xs px-2 py-0.5 rounded-full">
                    {user.role}
                  </span>
                </div>
                <button
                  onClick={logout}
                  className="text-sm text-slate-400 hover:text-white transition-colors"
                >
                  Logout
                </button>
              </div>
            ) : mounted ? (
              <div className="flex items-center space-x-2">
                {navLink("/login", "Login")}
                <Link href="/register" className="btn-primary text-sm !py-2 !px-4">
                  Sign Up
                </Link>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </nav>
  );
}
