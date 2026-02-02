import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Roles from "@/pages/Roles";
import { rolesData } from "@/pages/rolesData";

describe("Roles", () => {
  it("renders nav buttons and role cards", () => {
    render(
      <MemoryRouter>
        <Roles />
      </MemoryRouter>
    );

    expect(screen.getByRole("button", { name: "Reports" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Settings" })).toBeInTheDocument();

    rolesData.forEach((role) => {
      expect(screen.getByText(role.title)).toBeInTheDocument();
    });
  });
});
