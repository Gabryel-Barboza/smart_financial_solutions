import { navItems } from '../../data/navData';

const Navbar = ({ selectedNav, setSelectedNav }) => (
  <header className="flex lg:hidden items-center justify-between p-4 bg-white shadow-md">
    <div className="flex items-center space-x-2">
      <svg
        className="w-6 h-6 text-blue-600"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M9 19V6l12-3v14M9 19c-1.33 0-2.5-.56-3.33-1.4L2 14v4c0 2.21 1.79 4 4 4h12c1.33 0 2.5-.56 3.33-1.4L22 18V6l-3 1.5"
        ></path>
      </svg>
      <span className="text-lg font-bold text-gray-800">Agent Fiscal</span>
    </div>
    <div className="relative">
      <select
        className="p-2 border rounded-lg text-sm bg-gray-50 focus:ring-blue-500 focus:border-blue-500"
        value={selectedNav}
        onChange={(e) => setSelectedNav(e.target.value)}
      >
        {navItems.map((item) => (
          <option key={item.name} value={item.name}>
            {item.name}
          </option>
        ))}
      </select>
    </div>
  </header>
);

export default Navbar;
