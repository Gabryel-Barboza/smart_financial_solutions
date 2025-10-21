import type { Dispatch, SetStateAction } from 'react';

import { FaFileZipper } from 'react-icons/fa6';

import { navItems } from '../../data/navData';

interface Props {
  selectedNav: string;
  setSelectedNav: Dispatch<SetStateAction<string>>;
}

const Navbar = ({ selectedNav, setSelectedNav }: Props) => (
  <header className="flex lg:hidden items-center justify-between p-4 bg-white shadow-md">
    <div className="flex items-center text-gray-800 space-x-2">
      <FaFileZipper />
      <span className="text-lg font-bold">Agente Fiscal</span>
    </div>
    <div className="relative">
      <select
        className="p-2 border rounded-lg text-sm text-gray-800 bg-gray-50 focus:ring-blue-500 focus:border-blue-500"
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
