import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Matches from "./components/layout/Matches";
import Roles from "./pages/Roles";
import NotFound from "./pages/NotFound";
import Mode from "./pages/Mode";
import Core from "./components/layout/Core";
import BusinessPortal from "./pages/BusinessPortal";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Select Mode */}
          <Route path="/" element={<Mode/>}/>
          {/* Career profile routes */}
          <Route path="/portal" element={<Index />} />
          <Route path="/matches" element={<Matches />} />
          <Route path="/cv" element={<Core/>}/>
          
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />

          {/* Staffing/business routes */}
          <Route path="/staffing" element={<BusinessPortal />} />
          <Route path="/roles" element={<Roles />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
