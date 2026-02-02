export const rolesStats = [
  { label: "Total Project Roles", value: 42, change: "+2.4%", up: true },
  { label: "Open Positions", value: 12, change: "+5.1%", up: true },
  { label: "Filled (Last 30 days)", value: 30, change: "-1.2%", up: false },
];

export const rolesData = [
  {
    title: "Senior Fullstack Engineer",
    project: "Neo-Banking Mobile App",
    client: "CloudScale Systems",
    status: "high-priority" as const,
    icon: "code" as const,
    applicants: [
      { image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=50&h=50&fit=crop&crop=face" },
      { image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=50&h=50&fit=crop&crop=face" },
      { image: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=50&h=50&fit=crop&crop=face" },
      { image: "" },
      { image: "" },
      { image: "" },
      { image: "" },
    ],
  },
  {
    title: "Lead Product Designer",
    project: "Design System 2.0",
    client: "MetaLogix",
    status: "interviewing" as const,
    icon: "design" as const,
    applicants: [
      { image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=50&h=50&fit=crop&crop=face" },
      { image: "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=50&h=50&fit=crop&crop=face" },
      { image: "" },
      { image: "" },
    ],
  },
  {
    title: "Data Architect",
    project: "Big Data Migration",
    client: "FinServ Global",
    status: "pending" as const,
    icon: "data" as const,
    applicants: [],
  },
];

export const rolesTabs = ["Client", "Project", "Roles", "Documents"];
