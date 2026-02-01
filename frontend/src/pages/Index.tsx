import { NavLink } from "@/components/NavLink";
import { DarkSidebar } from "@/components/layout/DarkSidebar";
import { ProfileCard, SkillAnalysisCard } from "@/components/cards/ProfileCard";
import { CourseCard } from "@/components/cards/CourseCard";
import { Button } from "@/components/ui/button";
import { Bell, Settings, FileCheck, File, Award, Upload, Download, Eye } from "lucide-react";

const documents = [
  {
    name: "Employment_Contract_2024.pdf",
    status: "Signed",
    statusColor: "text-success",
    icon: File,
    date: "Oct 12, 2023",
  },
  {
    name: "PMP_Certification_Renewal.pdf",
    status: "Pending Review",
    statusColor: "text-warning",
    icon: Award,
    date: "Jan 05, 2024",
  },
  {
    name: "Annual_Performance_Review_Q4.pdf",
    status: "Completed",
    statusColor: "text-success",
    icon: FileCheck,
    date: "Dec 20, 2023",
  },
];

const courses = [
  {
    title: "Advanced Scrum Master",
    category: "Project Management",
    image: "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop",
    progress: 45,
    isStarted: true,
  },
  {
    title: "Stakeholder Communication",
    category: "Soft Skills",
    image: "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=400&h=200&fit=crop",
    description: "Master the art of presenting complex data to C-level executives.",
  },
  {
    title: "GenAI Foundations for Managers",
    category: "Technical",
    image: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=200&fit=crop",
    description: "Leverage LLMs to automate project workflows and documentation.",
  },
];

export default function Index() {
  return (
    <div className="flex h-screen overflow-hidden dark">
      {/* Left Panel: AI Interaction Hub */}
      <DarkSidebar
        userName="Sarah Jenkins"
        userRole="Senior Project Manager"
        userImage="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=face"
      />

      {/* Right Panel: Dashboard Content */}
      <main className="flex-1 h-full bg-background overflow-y-auto">
        {/* Header */}
        <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md px-10 py-6 border-b border-border flex justify-between items-center">
          <nav className="flex gap-8">
            <NavLink 
              to="/" 
              className="text-muted-foreground font-medium pb-1 transition-colors hover:text-foreground"
              activeClassName="text-primary font-bold border-b-2 border-primary"
            >
              Dashboard
            </NavLink>
            <NavLink 
              to="/matches" 
              className="text-muted-foreground font-medium pb-1 transition-colors hover:text-foreground"
              activeClassName="text-primary font-bold border-b-2 border-primary"
            >
              Growth Path
            </NavLink>
            <NavLink 
              to="/matches" 
              className="text-muted-foreground font-medium pb-1 transition-colors hover:text-foreground"
              activeClassName="text-primary font-bold border-b-2 border-primary"
            >
              Opportunities
            </NavLink>
          </nav>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
              <Bell className="size-5" />
            </Button>
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
              <Settings className="size-5" />
            </Button>
          </div>
        </header>

        <div className="p-10 max-w-6xl mx-auto space-y-12">
          {/* Profile & Skills Section */}
          <section>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold">You - Profile & Skills</h3>
              <Button variant="link" className="text-primary font-semibold">
                Edit Profile
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <ProfileCard
                name="Sarah Jenkins"
                role="Senior Project Manager"
                department="Staffing Tech Div."
                image="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&crop=face"
                skills={["Agile Leadership", "Data Visualization", "Stakeholder Mgmt", "Python", "SQL", "Team Building", "Scrum"]}
                verified
              />
              <SkillAnalysisCard skillName="Python" progress={72} improvement={15} />
            </div>
          </section>

          {/* Learning Recommendations */}
          <section>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold">Recommended Learning</h3>
              <Button variant="link" className="text-primary font-semibold">
                Explore Catalog
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {courses.map((course, idx) => (
                <CourseCard key={idx} {...course} />
              ))}
            </div>
          </section>

          {/* Documents Section */}
          <section className="pb-20">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold">Recent Documents</h3>
              <Button variant="link" className="text-primary font-semibold flex items-center gap-1">
                <Upload className="size-4" />
                Upload New
              </Button>
            </div>
            <div className="bg-card rounded-2xl shadow-sm border border-border overflow-hidden">
              <table className="w-full text-left">
                <thead className="bg-secondary/50 border-b border-border">
                  <tr>
                    <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase">Document Name</th>
                    <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase">Status</th>
                    <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase">Upload Date</th>
                    <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {documents.map((doc, idx) => (
                    <tr key={idx} className="hover:bg-secondary/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <doc.icon className="size-4 text-muted-foreground" />
                          <span className="font-medium">{doc.name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`text-xs font-bold flex items-center gap-1 ${doc.statusColor}`}>
                          <FileCheck className="size-3" />
                          {doc.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{doc.date}</td>
                      <td className="px-6 py-4 text-right">
                        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-primary">
                          {doc.status === "Pending Review" ? <Eye className="size-4" /> : <Download className="size-4" />}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="bg-secondary/50 p-4 text-center">
                <Button variant="link" className="text-sm font-bold text-muted-foreground hover:text-foreground">
                  View All Documents
                </Button>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
